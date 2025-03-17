
#
# Main component of TF Micro project 'micro_speech'.
#

idf_component_register(
    SRCS main.c validation.c
    PRIV_REQUIRES spi_flash
    INCLUDE_DIRS "")
