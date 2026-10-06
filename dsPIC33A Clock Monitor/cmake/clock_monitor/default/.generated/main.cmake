include("${CMAKE_CURRENT_LIST_DIR}/rule.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/file.cmake")

set(clock_monitor_default_library_list )

# Handle files with suffix s, for group default-XC-DSC
if(clock_monitor_default_default_XC_DSC_FILE_TYPE_assemble)
add_library(clock_monitor_default_default_XC_DSC_assemble OBJECT ${clock_monitor_default_default_XC_DSC_FILE_TYPE_assemble})
    clock_monitor_default_default_XC_DSC_assemble_rule(clock_monitor_default_default_XC_DSC_assemble)
    list(APPEND clock_monitor_default_library_list "$<TARGET_OBJECTS:clock_monitor_default_default_XC_DSC_assemble>")

endif()

# Handle files with suffix S, for group default-XC-DSC
if(clock_monitor_default_default_XC_DSC_FILE_TYPE_assemblePreproc)
add_library(clock_monitor_default_default_XC_DSC_assemblePreproc OBJECT ${clock_monitor_default_default_XC_DSC_FILE_TYPE_assemblePreproc})
    clock_monitor_default_default_XC_DSC_assemblePreproc_rule(clock_monitor_default_default_XC_DSC_assemblePreproc)
    list(APPEND clock_monitor_default_library_list "$<TARGET_OBJECTS:clock_monitor_default_default_XC_DSC_assemblePreproc>")

endif()

# Handle files with suffix c, for group default-XC-DSC
if(clock_monitor_default_default_XC_DSC_FILE_TYPE_compile)
add_library(clock_monitor_default_default_XC_DSC_compile OBJECT ${clock_monitor_default_default_XC_DSC_FILE_TYPE_compile})
    clock_monitor_default_default_XC_DSC_compile_rule(clock_monitor_default_default_XC_DSC_compile)
    list(APPEND clock_monitor_default_library_list "$<TARGET_OBJECTS:clock_monitor_default_default_XC_DSC_compile>")

endif()

# Handle files with suffix cpp, for group default-XC-DSC
if(clock_monitor_default_default_XC_DSC_FILE_TYPE_compile_cpp)
add_library(clock_monitor_default_default_XC_DSC_compile_cpp OBJECT ${clock_monitor_default_default_XC_DSC_FILE_TYPE_compile_cpp})
    clock_monitor_default_default_XC_DSC_compile_cpp_rule(clock_monitor_default_default_XC_DSC_compile_cpp)
    list(APPEND clock_monitor_default_library_list "$<TARGET_OBJECTS:clock_monitor_default_default_XC_DSC_compile_cpp>")

endif()

# Handle files with suffix s, for group default-XC-DSC
if(clock_monitor_default_default_XC_DSC_FILE_TYPE_dependentObject)
add_library(clock_monitor_default_default_XC_DSC_dependentObject OBJECT ${clock_monitor_default_default_XC_DSC_FILE_TYPE_dependentObject})
    clock_monitor_default_default_XC_DSC_dependentObject_rule(clock_monitor_default_default_XC_DSC_dependentObject)
    list(APPEND clock_monitor_default_library_list "$<TARGET_OBJECTS:clock_monitor_default_default_XC_DSC_dependentObject>")

endif()

# Handle files with suffix elf, for group default-XC-DSC
if(clock_monitor_default_default_XC_DSC_FILE_TYPE_bin2hex)
add_library(clock_monitor_default_default_XC_DSC_bin2hex OBJECT ${clock_monitor_default_default_XC_DSC_FILE_TYPE_bin2hex})
    clock_monitor_default_default_XC_DSC_bin2hex_rule(clock_monitor_default_default_XC_DSC_bin2hex)
    list(APPEND clock_monitor_default_library_list "$<TARGET_OBJECTS:clock_monitor_default_default_XC_DSC_bin2hex>")

endif()


# Main target for this project
add_executable(clock_monitor_default_image_TlAsTVSH ${clock_monitor_default_library_list})

if(NOT CMAKE_HOST_WIN32)
    set_target_properties(clock_monitor_default_image_TlAsTVSH PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${clock_monitor_default_output_dir}")
endif()
set_target_properties(clock_monitor_default_image_TlAsTVSH PROPERTIES
    OUTPUT_NAME "default"
    SUFFIX ".elf")
target_link_libraries(clock_monitor_default_image_TlAsTVSH PRIVATE ${clock_monitor_default_default_XC_DSC_FILE_TYPE_link})
# Add the link options from the rule file.
clock_monitor_default_link_rule( clock_monitor_default_image_TlAsTVSH)

# Call bin2hex function from the rule file
clock_monitor_default_bin2hex_rule(clock_monitor_default_image_TlAsTVSH)
if(CMAKE_HOST_WIN32)
    add_custom_command(
        TARGET clock_monitor_default_image_TlAsTVSH
        POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory ${clock_monitor_default_output_dir}
        COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:clock_monitor_default_image_TlAsTVSH> ${clock_monitor_default_output_dir}/${clock_monitor_default_original_image_name}
        BYPRODUCTS ${clock_monitor_default_output_dir}/${clock_monitor_default_original_image_name}
        COMMENT "Copying elf to out location")
    set_property(
        TARGET clock_monitor_default_image_TlAsTVSH
        APPEND PROPERTY ADDITIONAL_CLEAN_FILES
        ${clock_monitor_default_output_dir}/${clock_monitor_default_original_image_name})
endif()


