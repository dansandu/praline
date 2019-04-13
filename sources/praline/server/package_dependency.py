from praline.common.algorithm.general import cartesian_product
from praline.common.algorithm.graph.multiworld_traversal import multiworld_depth_first_traversal
from praline.common.file_system import join, split_files_in_directory
from praline.common.packaging import dependant_packages_from_package, package_metadata
from praline.common.tracing import trace


class HotPackage:
    def __init__(self, package, identifier, version, wildcard):
        self.package = package
        self.identifier = identifier
        self.version = version
        self.wildcard = wildcard

    def matches(self, other):
        if self.identifier != other.identifier:
            return False
        for i in range(len(self.wildcard)):
            if self.wildcard[i] and self.version[i] <= other.version[i] or not self.wildcard[i] and self.version[i] == other.version[i]:
                continue
            else:
                return False
        return True

    def __str__(self):
        return self.package

    def __repr__(self):
        return self.package


@trace
def hot_packages_in_directory(directory):
    metadata = [package_metadata(package, none_on_failure=True) for _, package in split_files_in_directory(directory)]
    return [HotPackage(m['package'], m['identifier'], m['version'], m['wildcard']) for m in metadata if m]


@trace
def get_matching_packages_in_descending_order(wildcard_package, candidate_hot_packages):
    m = package_metadata(wildcard_package)
    hot_wildcard_package = HotPackage(m['package'], m['identifier'], m['version'], m['wildcard'])
    matching_hot_packages = [candidate for candidate in candidate_hot_packages if hot_wildcard_package.matches(candidate)]
    return [hot_package.package for hot_package in sorted(matching_hot_packages, key=lambda p: p.version, reverse=True)]


def version_conflict_in_dependency_tree(package, dependency_tree):
    package_identifier, package_version = package.rsplit('-', 1)
    for dependency in dependency_tree:
        dependency_identifier, dependency_version = dependency.rsplit('-', 1)
        if package_identifier == dependency_identifier and package_version != dependency_version:
            return True
    return False


@trace
def get_dependant_packages_recursively(root_package, root_package_depedencies, package_directory):
    candidate_hot_packages = hot_packages_in_directory(package_directory)

    def throw_on_cyclic_depedency(cyclic_dependencies):
        raise RuntimeError(f"artifact '{root_package}' has cyclic dependencies {cyclic_dependencies}")

    def visitor(package):
        if package is not root_package:
            package_path = join(package_directory, package)
            wildcard_dependencies = dependant_packages_from_package(package_path, 'main')
        else:
            wildcard_dependencies = root_package_depedencies
        fixed_dependencies = []
        for wildcard_dependency in wildcard_dependencies:
            matching_dependencies = get_matching_packages_in_descending_order(wildcard_dependency, candidate_hot_packages)
            if not matching_dependencies:
                raise RuntimeError(f"couldn't find any package matching '{wildcard_dependency}' when solving dependencies for package '{root_package}'")
            fixed_dependencies.append(matching_dependencies)
        return cartesian_product(fixed_dependencies)

    dependency_trees = multiworld_depth_first_traversal(root_package, visitor, lambda a, b: not version_conflict_in_dependency_tree(a, b), throw_on_cyclic_depedency)
    if not dependency_trees:
        raise RuntimeError(f"could not solve dependencies for '{root_package}' due to version conflicts")
    dependencies = [dependency for dependency in dependency_trees[0].tree]
    dependencies.remove(root_package)
    return dependencies
