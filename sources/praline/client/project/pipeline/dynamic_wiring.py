from praline.common.file_system import basename, current_working_directory, files_in_directory, join

source_root = join(current_working_directory(), 'sources')


def run_unit_tests_wiring(stages):
    if any(f for f in files_in_directory(source_root) if f.endswith('.test.cpp')):
        stages['package_executable'].consumes.extend(stages['test'].produces)
        stages['package_header_only'].consumes.extend(stages['test'].produces)
        stages['package_library'].consumes.extend(stages['test'].produces)
        stages['main'].consumes.extend(stages['test'].produces)


def format_code_wiring(stages):
    stages['package_header_only'].consumes.extend(stages['format_headers'].produces)
    stages['package_library'].consumes.extend(stages['format_headers'].produces)
    stages['compile_main_sources'].consumes.extend(stages['format_headers'].produces)
    stages['compile_main_sources'].consumes.extend(stages['format_main_sources'].produces)
    stages['compile_test_sources'].consumes.extend(stages['format_headers'].produces)
    stages['compile_test_sources'].consumes.extend(stages['format_test_sources'].produces)


def deploy_wiring(stages):    
    main_sources = [f for f in files_in_directory(source_root) if f.endswith('.cpp') and not f.endswith('.test.cpp')]
    if not main_sources:
        stages['deploy'].consumes.extend(stages['deploy_header_only'].produces)
    elif any(s for s in main_sources if basename(s) == 'executable.cpp'):
        stages['deploy'].consumes.extend(stages['deploy_executable'].produces)
    else:
        stages['deploy'].consumes.extend(stages['deploy_library'].produces)
