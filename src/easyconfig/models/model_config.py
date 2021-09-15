class EasyBaseConfig:
    validate_all = True     # validate field defaults
    use_enum_values = True  # populate models with the value property of enums, rather than the raw enum
    underscore_attrs_are_private = True  # treat any underscore non-class var attrs as private, or leave them as is
