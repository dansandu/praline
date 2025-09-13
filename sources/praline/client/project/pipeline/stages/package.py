from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common.package import manifest_file_name, pack, write_artifact_manifest
from praline.common.file_system import join, relative_path, is_subpath


@stage(
    requirements=[
        'project_directories', 'main_resources', 'main_headers', 'main_library', 
        'main_library_interface', 'main_library_symbols_table', 'main_executable', 
        'main_farseer_cpp_headers', 'main_executable_symbols_table', 'tests_passed',
    ],
    output=['package'], 
    exposed=True
)
def package(arguments: StageArguments):
    file_system       = arguments.file_system
    artifact_manifest = arguments.artifact_manifest
    project_structure = arguments.project_structure
    resources         = arguments.resources

    project_root                = project_structure.project_directory
    main_sources_root           = project_structure.main_sources_root
    main_generated_sources_root = project_structure.main_generated_sources_root
    target_root                 = project_structure.target_root
    manifest_file_path          = join(target_root, manifest_file_name)

    main_executable               = resources['main_executable']
    main_executable_symbols_table = resources['main_executable_symbols_table']
    main_library                  = resources['main_library']
    main_library_interface        = resources['main_library_interface']
    main_library_symbols_table    = resources['main_library_symbols_table']

    write_artifact_manifest(file_system, manifest_file_path, artifact_manifest)

    package_files = []

    package_files.extend(
        (path, relative_path(path, project_root)) for path in resources['main_resources'])

    package_files.extend(
        (path, join('headers', relative_path(path, main_sources_root))) for path in resources['main_headers'])

    package_files.extend(
        (path, join('headers', relative_path(path, main_generated_sources_root))) for path in resources['main_farseer_cpp_headers'])

    package_files.append((manifest_file_path, manifest_file_name))

    if main_executable != None:
        package_files.append((main_executable, relative_path(main_executable, target_root)))
        if main_executable_symbols_table != None:
            package_files.append((main_executable_symbols_table, relative_path(main_executable_symbols_table, target_root)))

    if main_library != None:
        package_files.append((main_library, relative_path(main_library, target_root)))
        if main_library_interface != None:
            package_files.append((main_library_interface, relative_path(main_library_interface, target_root)))
        if main_library_symbols_table != None:
            package_files.append((main_library_symbols_table, relative_path(main_library_symbols_table, target_root)))
    
    package_path = join(project_structure.packages_root, artifact_manifest.get_package_file_name_and_instantiate_snapshot())

    pack(file_system, package_path, package_files, arguments.progress_bar_supplier)

    resources['package'] = package_path
