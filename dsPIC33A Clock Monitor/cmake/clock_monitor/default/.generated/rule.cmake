# The following functions contains all the flags passed to the different build stages.

set(PACK_REPO_PATH "C:/Users/c08282/.mchp_packs" CACHE PATH "Path to the root of a pack repository.")

function(clock_monitor_default_default_XC_DSC_assemble_rule target)
    set(options
        "-g"
        "-mcpu=33AK512MPS512"
        "-Wa,--defsym=__MPLAB_BUILD=1,--defsym=__MPLAB_DEBUG=1,--defsym=__DEBUG=1,-g,--no-relax"
        "-mdfp=${PACK_REPO_PATH}/Microchip/dsPIC33AK-MP_DFP/1.4.260/xc16")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG=1"
        PRIVATE "XPRJ_default=default")
    target_include_directories(${target} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../..")
endfunction()
function(clock_monitor_default_default_XC_DSC_assemblePreproc_rule target)
    set(options
        "-x"
        "assembler-with-cpp"
        "-g"
        "-mcpu=33AK512MPS512"
        "-Wa,--defsym=__MPLAB_BUILD=1,--defsym=__MPLAB_DEBUG=1,--defsym=__DEBUG=1,-g,--no-relax"
        "-mdfp=${PACK_REPO_PATH}/Microchip/dsPIC33AK-MP_DFP/1.4.260/xc16")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG=1"
        PRIVATE "XPRJ_default=default")
    target_include_directories(${target}
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../.."
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../..")
endfunction()
function(clock_monitor_default_default_XC_DSC_compile_rule target)
    set(options
        "-g"
        "-mcpu=33AK512MPS512"
        "-O0"
        "-msmart-io=1"
        "-Wall"
        "-msfr-warn=off"
        "-mdfp=${PACK_REPO_PATH}/Microchip/dsPIC33AK-MP_DFP/1.4.260/xc16")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG"
        PRIVATE "XPRJ_default=default")
    target_include_directories(${target} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../..")
endfunction()
function(clock_monitor_default_default_XC_DSC_compile_cpp_rule target)
    set(options
        "-g"
        "${CC_PRE}"
        "${DEBUGGER_NAME_AS_MACRO}"
        "-fframe-base-loclist"
        "-mcpu=33AK512MPS512"
        "-frtti"
        "-fexceptions"
        "-fno-check-new"
        "-fenforce-eh-specs"
        "-fno-common"
        "-mdfp=${PACK_REPO_PATH}/Microchip/dsPIC33AK-MP_DFP/1.4.260/xc16")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG"
        PRIVATE "XPRJ_default=default")
endfunction()
function(clock_monitor_default_dependentObject_rule target)
    set(options
        "-c"
        "-mcpu=33AK512MPS512"
        "-mdfp=${PACK_REPO_PATH}/Microchip/dsPIC33AK-MP_DFP/1.4.260/xc16")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
endfunction()
function(clock_monitor_default_link_rule target)
    set(options
        "-g"
        "-mcpu=33AK512MPS512"
        "-Wl,--script=p33AK512MPS512.gld,--local-stack,--defsym=__MPLAB_BUILD=1,--defsym=__MPLAB_DEBUG=1,--defsym=__DEBUG=1,-D__DEBUG=__DEBUG,--stack=16,--check-sections,--data-init,--pack-data,--handles,--isr,--no-gc-sections,--fill-upper=0,--stackguard=16,--library-path=${CMAKE_CURRENT_SOURCE_DIR}/../../..,--no-force-link,--smart-io,-Map=clock_monitor.map,--report-mem,--cref,--memorysummary,memoryfile.xml"
        "-mdfp=${PACK_REPO_PATH}/Microchip/dsPIC33AK-MP_DFP/1.4.260/xc16")
    list(REMOVE_ITEM options "")
    target_link_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG=__DEBUG"
        PRIVATE "XPRJ_default=default")
endfunction()
function(clock_monitor_default_bin2hex_rule target)
    add_custom_target(
        clock_monitor_default_Bin2Hex ALL
        COMMAND ${MP_BIN2HEX} ${clock_monitor_default_image_name} -a -mdfp=${PACK_REPO_PATH}/Microchip/dsPIC33AK-MP_DFP/1.4.260/xc16
        WORKING_DIRECTORY ${clock_monitor_default_output_dir}
        BYPRODUCTS "${clock_monitor_default_output_dir}/${clock_monitor_default_image_base_name}.hex"
        COMMENT "Convert build file to .hex")
    add_dependencies(clock_monitor_default_Bin2Hex ${target})
endfunction()
