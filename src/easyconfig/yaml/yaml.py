import ruamel.yaml  # type: ignore

yaml_rt = ruamel.yaml.YAML(typ='rt')
yaml_safe = ruamel.yaml.YAML(typ='safe')

CommentedMap = ruamel.yaml.comments.CommentedMap
CommentedSeq = ruamel.yaml.comments.CommentedSeq

for __loader in (yaml_rt, yaml_safe):
    __loader.default_flow_style = False
    __loader.default_style = False
    __loader.width = 1_000_000
    __loader.allow_unicode = True
    __loader.sort_base_mapping_type_on_output = False
