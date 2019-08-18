import noma.config as cfg_file


class DotNotation(dict):
    """dot.notation access to dictionary attributes"""
    def __getattr__(self, attr):
        return self.get(attr)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


cfg = {}
cfg.update(vars(cfg_file))
cfg = DotNotation(cfg)
