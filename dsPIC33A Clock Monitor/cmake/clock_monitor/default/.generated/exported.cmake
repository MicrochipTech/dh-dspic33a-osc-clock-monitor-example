set(DEPENDENT_MP_BIN2HEXclock_monitor_default_TlAsTVSH "c:/Program Files/Microchip/xc-dsc/v4.00/bin/xc-dsc-bin2hex.exe")
set(DEPENDENT_DEPENDENT_TARGET_ELFclock_monitor_default_TlAsTVSH "${CMAKE_CURRENT_LIST_DIR}/../../../../out/clock_monitor/default.elf")
set(DEPENDENT_TARGET_DIRclock_monitor_default_TlAsTVSH "${CMAKE_CURRENT_LIST_DIR}/../../../../out/clock_monitor")
set(DEPENDENT_BYPRODUCTSclock_monitor_default_TlAsTVSH ${DEPENDENT_TARGET_DIRclock_monitor_default_TlAsTVSH}/${sourceFileNameclock_monitor_default_TlAsTVSH}.s)
add_custom_command(
    OUTPUT ${DEPENDENT_TARGET_DIRclock_monitor_default_TlAsTVSH}/${sourceFileNameclock_monitor_default_TlAsTVSH}.s
    COMMAND ${DEPENDENT_MP_BIN2HEXclock_monitor_default_TlAsTVSH} ${DEPENDENT_DEPENDENT_TARGET_ELFclock_monitor_default_TlAsTVSH} --image ${sourceFileNameclock_monitor_default_TlAsTVSH} ${addressclock_monitor_default_TlAsTVSH} ${modeclock_monitor_default_TlAsTVSH} -mdfp=C:/Users/c08282/.mchp_packs/Microchip/dsPIC33AK-MP_DFP/1.4.260/xc16 
    WORKING_DIRECTORY ${DEPENDENT_TARGET_DIRclock_monitor_default_TlAsTVSH}
    DEPENDS ${DEPENDENT_DEPENDENT_TARGET_ELFclock_monitor_default_TlAsTVSH})
add_custom_target(
    dependent_produced_source_artifactclock_monitor_default_TlAsTVSH 
    DEPENDS ${DEPENDENT_TARGET_DIRclock_monitor_default_TlAsTVSH}/${sourceFileNameclock_monitor_default_TlAsTVSH}.s
    )
