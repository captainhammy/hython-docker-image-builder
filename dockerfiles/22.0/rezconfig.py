pip_install_remaps = [
    {
        "record_path": r"{p}{s}{p}{s}(share{s}.*)",
        "pip_install": r"\1",
        "rez_install": r"\1",
    },
    {
        "record_path": r"^{p}{s}{p}{s}(LICENSE.txt)",
        "pip_install": r"\1",
        "rez_install": r"\1",
    },

    {
        "record_path": r"^{p}{s}{p}{s}(include{s}.*)",
        "pip_install": r"\1",
        "rez_install": r"\1",
    },
    {
        "record_path": r"^{p}{s}{p}{s}(bin{s}.*)",
        "pip_install": r"\1",
        "rez_install": r"\1",
    },
    {
        "record_path": r"^{p}{s}{p}{s}(share{s}.*)",
        "pip_install": r"\1",
        "rez_install": r"\1",
    },

    {
        "record_path": r"^{p}{s}{p}{s}(etc{s}.*)",
        "pip_install": r"\1",
        "rez_install": r"\1",
    },

    {
        "record_path": r"^{p}{s}{p}{s}lib/python/(.*)",
        "pip_install": r"\1",
        "rez_install": r"python/\1",
    }
]
