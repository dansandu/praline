from praline.common import ProjectStructure

from os.path import join


project_structure_dummy = ProjectStructure(
    project_directory='project',
    resources_root=join('project', 'resources'),
    sources_root=join('project', 'sources'),
    target_root=join('project', 'target'),
    objects_root=join('project', 'target', 'objects'),
    executables_root=join('project', 'target', 'executables'),
    libraries_root=join('project', 'target', 'libraries'),
    libraries_interfaces_root=join('project', 'target', 'libraries_interfaces'),
    symbols_tables_root=join('project', 'target', 'symbols_tables'),
    external_root=join('project', 'target', 'external'),
    external_packages_root=join('project', 'target', 'external', 'packages'),
    external_headers_root=join('project', 'target', 'external', 'headers'),
    external_executables_root=join('project', 'target', 'external', 'executables'),
    external_libraries_root=join('project', 'target', 'external', 'libraries'),
    external_libraries_interfaces_root=join('project', 'target', 'external', 'libraries_interfaces'),
    external_symbols_tables_root=join('project', 'target', 'external', 'symbols_tables'),
)
