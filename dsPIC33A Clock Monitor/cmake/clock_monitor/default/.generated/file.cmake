# The following variables contains the files used by the different stages of the build process.
set(clock_monitor_default_default_XC_DSC_FILE_TYPE_assemble)
set_source_files_properties(${clock_monitor_default_default_XC_DSC_FILE_TYPE_assemble} PROPERTIES LANGUAGE ASM)

# For assembly files, add "." to the include path for each file so that .include with a relative path works
foreach(source_file ${clock_monitor_default_default_XC_DSC_FILE_TYPE_assemble})
        set_source_files_properties(${source_file} PROPERTIES INCLUDE_DIRECTORIES "$<PATH:NORMAL_PATH,$<PATH:REMOVE_FILENAME,${source_file}>>")
endforeach()

set(clock_monitor_default_default_XC_DSC_FILE_TYPE_assemblePreproc)
set_source_files_properties(${clock_monitor_default_default_XC_DSC_FILE_TYPE_assemblePreproc} PROPERTIES LANGUAGE ASM)

# For assembly files, add "." to the include path for each file so that .include with a relative path works
foreach(source_file ${clock_monitor_default_default_XC_DSC_FILE_TYPE_assemblePreproc})
        set_source_files_properties(${source_file} PROPERTIES INCLUDE_DIRECTORIES "$<PATH:NORMAL_PATH,$<PATH:REMOVE_FILENAME,${source_file}>>")
endforeach()

set(clock_monitor_default_default_XC_DSC_FILE_TYPE_compile
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../adc.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../clock.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../clock_monitor.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../config_bits.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../demo_app.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../gpio.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../main.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../sccp1.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../sccp2.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../tmr1_tick.c")
set_source_files_properties(${clock_monitor_default_default_XC_DSC_FILE_TYPE_compile} PROPERTIES LANGUAGE C)
set(clock_monitor_default_default_XC_DSC_FILE_TYPE_compile_cpp)
set_source_files_properties(${clock_monitor_default_default_XC_DSC_FILE_TYPE_compile_cpp} PROPERTIES LANGUAGE CXX)
set(clock_monitor_default_default_XC_DSC_FILE_TYPE_link)
set(clock_monitor_default_default_XC_DSC_FILE_TYPE_bin2hex)
set(clock_monitor_default_image_name "default.elf")
set(clock_monitor_default_image_base_name "default")

# The output directory of the final image.
set(clock_monitor_default_output_dir "${CMAKE_CURRENT_SOURCE_DIR}/../../../out/clock_monitor")

# The full path to the final image.
set(clock_monitor_default_full_path_to_image ${clock_monitor_default_output_dir}/${clock_monitor_default_image_name})
