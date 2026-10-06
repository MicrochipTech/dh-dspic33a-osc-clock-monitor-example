# Additional clean files
cmake_minimum_required(VERSION 3.16)

if("${CONFIG}" STREQUAL "" OR "${CONFIG}" STREQUAL "")
  file(REMOVE_RECURSE
  "C:\\dsPIC33A VSCode Examples\\Clock Monitor\\dsPIC33A Clock Monitor\\out\\clock_monitor"
  )
endif()
