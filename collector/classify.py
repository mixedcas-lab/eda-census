"""Classification and spec extraction for analog/mixed-signal circuit design automation papers.

Covers automated sizing and topology synthesis, layout automation, synthesizable (standard-cell)
analog and mixed-signal circuits, circuit generators and compilers, and machine-learning methods
for circuit design. Pure functions (no network, no files); abstracts are inputs only and are never
written to the output.
"""
import re

I = re.IGNORECASE

# ---------------------------------------------------------------- relevance
# the circuit being designed: analog, mixed-signal, RF or memory circuits (not logic synthesis, FPGA mapping or timing)
AMS = re.compile(r"analog|mixed[- ]signal|\bAMS\b|\bA/MS\b|\bRF\b|op[- ]?amps?\b|operational (?:transconductance )?amplifiers?|"
                 r"\bOTAs?\b|amplifiers?|\bADCs?\b|\bDACs?\b|data converters?|\bPLLs?\b|\bDLLs?\b|\bLDOs?\b|regulators?|"
                 r"comparators?|bandgap|voltage references?|\bLNAs?\b|\bVCOs?\b|oscillators?|active[- ]RC|\bGm[- ]?C\b|analog filters?|"
                 r"transistor[- ]level|transistor sizing|device sizing|circuit sizing|custom circuits?|\bSRAM\b|memory (?:circuit|array|peripheral)|"
                 r"\bNAND\b|sense amplifiers?|power (?:converters?|management)|DC[-–]DC|charge pumps?|\bSAR\b|\bTDCs?\b|serdes|transceivers?", I)
# the automation: a design task that is automated ...
TASK = re.compile(r"design automation|automat\w*[- ](?:design|sizing|synthesis|layout|generat\w*|optimi[sz]ation|placement|routing|migration)|"
                  r"automatically (?:generated|designed|sized|synthesi[sz]ed|placed|routed)|(?:transistor|device|circuit|parameter|component) sizing|"
                  r"(?<!switch )(?<!switch-)sizing (?:of|for|method|methodology|algorithm|framework|tool|optimi[sz]ation)|(?:optimal|automatic|automated) sizing|topology (?:synthesis|generation|search|selection|optimi[sz]ation)|(?:analog|circuit|AMS) synthesis|"
                  r"layout (?:generation|generator|automation|synthesis|migration|retargeting|placement)|(?:analog|device|module|layout) (?:placement|routing)|"
                  r"(?:placement|routing) (?:algorithm|tool|method|framework|for analog)|placement and routing|place[- ]and[- ]route|"
                  r"(?:circuit|layout|netlist|design|code|front[- ]?end|PLL|ADC|DAC|LDO|SerDes|memory|SRAM|analog) (?:generators?|compilers?)|"
                  r"\bcompilers?\b|synthesi[sz]ed (?:[\w/-]+[- ]){0,4}?(?:PLLs?|ADCs?|DACs?|LDOs?|DLLs?|TDCs?|amplifiers?|regulators?|oscillators?|circuits?)\b|"
                  r"synthesi[sz]able|standard[- ]cell[- ]based|digital (?:design )?flow|auto[- ]?(?:generated|placed|routed)|"
                  r"design space exploration|yield (?:optimi|estimat|aware)|variation[- ]aware (?:design|sizing|optimi)|"
                  r"performance model(?:ing|s)? (?:of|for)|(?:framework|methodology|tool|flow) for (?:the )?(?:automated |automatic )?"
                  r"(?:design|sizing|optimi[sz]ation|synthesis)|(?:design|circuit|analog) optimi[sz]ation (?:framework|method|tool|algorithm)|"
                  r"LLM[- ](?:based|aided|assisted|driven|powered)|large language models? (?:for|in)|using (?:an? )?(?:LLM|large language)", I)
# ... or an optimization/learning method applied to designing (not calibrating or running) a circuit
METHOD = re.compile(r"reinforcement learning|bayesian optimi[sz]ation|\bGNNs?\b|graph neural|surrogate|evolutionary|genetic algorithm|"
                    r"particle swarm|\bPSO\b|differential evolution|simulated annealing|gm/I[Dd]|knowledge[- ]based|geometric programming|"
                    r"convex optimi[sz]ation|multi[- ]objective|machine[- ]learning|deep[- ]learning|neural[- ]network[- ](?:based|assisted)", I)
DESIGN = re.compile(r"\bdesign|sizing|optimi[sz]|synthes|topolog|layout", I)
EDA = re.compile(TASK.pattern + "|" + METHOD.pattern, I)    # used by the report's miss list
# words that look like automation but are circuits
NOT_EDA = re.compile(r"frequency synthesi[sz]er|direct[- ]digital (?:frequency )?synthes|\bDDFS\b|\bDDS\b|signal synthesis|"
                     r"waveform generat|(?:clock|pulse|ramp|function|signal|noise|random number|reference|bias|current) generators?|"
                     r"automatic (?:gain|frequency|level|exposure|offset) control|\bAGC\b|automatic[- ]calibration|auto[- ]?zero|"
                     r"logic synthesis|high[- ]level synthesis|\bFPGA\b|clock tree|timing (?:analysis|closure)|\bSTA\b|"
                     r"decimation filter|digital filter|\bFIR\b|\bIIR\b|adaptive filter|beamform", I)
NON_PAPER = re.compile(
    r"^(front cover|back cover|table of contents|contents|author index|index|"
    r"call for papers|editorial|guest editorial|reviewers|session \d+ overview|"
    r"(?:tutorials?|short course|evening (?:event|session)|forum|panel|keynote)(?=\s*:|\s*$)|"
    r"(ieee )?(transactions|journal) .*information|blank page|copyright|in this issue)\b", I)


DIGITAL_EDA = re.compile(r"clock tree|logic synthesis|high[- ]level synthesis|\bFPGAs?\b|sleep transistor|power gating|timing (?:analysis|closure)|\bSTA\b|"
                         r"standard[- ]cell librar|gate[- ]level|\bRTL\b|netlist partition", I)


def relevance(title, abstract):
    """'core': the paper is about automating the design of an analog/mixed-signal/memory circuit; 'related': the
    title is a circuit and the abstract says it was generated or synthesized automatically; else None."""
    t = title or ""
    if DIGITAL_EDA.search(t) and not re.search(r"analog|mixed[- ]signal|\bAMS\b", t, I):
        return None
    clean = NOT_EDA.sub(" ", t)
    if AMS.search(clean) and (TASK.search(clean) or (METHOD.search(clean) and DESIGN.search(clean)
                                                     and not re.search(r"calibrat|compensat|correction|detection|classif", clean, I))):
        return "core"
    if re.search(r"(?:analog|circuit|AMS) design automation|analog EDA|\bAMS\b.*\bEDA\b", t, I):
        return "core"
    a = NOT_EDA.sub(" ", abstract or "")
    if AMS.search(clean) and re.search(r"synthesi[sz]able|standard[- ]cell|automatically generated|automated (?:layout|design|sizing)|"
                                       r"(?:design|layout) automation|place[- ]and[- ]route|digital (?:design )?flow", a, I):
        return "related"
    return None


# ------------------------------------------------------------- type / task / method / circuit
ML_RX = re.compile(r"machine[- ]learning|deep[- ]learning|neural[- ]network|reinforcement learning|\bRL\b|\bGNNs?\b|graph neural|"
                   r"\bLLMs?\b|large language|transformer[- ]based|\bAI\b|learning[- ]based|\bagents?\b|bayesian optimi[sz]ation|"
                   r"\bBO\b|gaussian process|surrogate", I)


def da_type(title, abstract):
    first = " ".join(re.split(r"(?<=[.!?])\s+", abstract or "")[:2])
    return "ML-based" if ML_RX.search(title or "") or ML_RX.search(first) else "Conventional"


ARCH_RULES = [   # the design task
    ("Sizing/optimization",  r"sizing|parameter optimi|design optimi|optimi[sz]ation (?:framework|method|algorithm|tool)|"
                             r"multi[- ]objective|bayesian optimi|reinforcement learning|evolutionary|genetic|particle swarm|\bPSO\b|gm/I[Dd]"),
    ("Topology synthesis",   r"topology|circuit synthesis|analog synthesis|structure (?:synthesis|generation)|netlist generation"),
    ("Layout automation",    r"layout|placement|routing|place[- ]and[- ]route|floorplan|\bP&R\b|parasitic"),
    ("Synthesizable/cell-based", r"synthesi[sz]able|standard[- ]cell|\bcell[- ]based|digital (?:design )?flow|auto[- ]?(?:placed|routed)"),
    ("Generator/compiler",   r"compiler|generator|template|\bPCell|procedural|parameteri[sz]ed (?:layout|design)"),
    ("Modeling/surrogate",   r"performance model|behavio(?:u)?ral model|surrogate|regression|prediction|estimat"),
    ("Yield/variation",      r"yield|variation|mismatch|monte[- ]carlo|process corner|\bPVT\b|reliability|aging"),
    ("Verification/test",    r"verification|testing|test generation|fault|coverage|formal"),
]
ARCH_RX = [(n, re.compile(p, I)) for n, p in ARCH_RULES]

MOD_RULES = [    # the method
    ("Reinforcement learning", r"reinforcement learning|\bRL\b|\bDDPG\b|\bPPO\b|actor[- ]critic|Q[- ]learning"),
    ("Bayesian optimization",  r"bayesian optimi|\bBO\b|gaussian process|\bGPs?\b|acquisition function|\bTuRBO"),
    ("Graph neural network",   r"\bGNNs?\b|graph neural|graph convolution|\bGCN|graph[- ]?RL|graph[- ]based (?:RL|learning|representation)"),
    ("LLM",                    r"\bLLMs?\b|large language|\bGPT|language model|\bagents?\b|chat"),
    ("Neural network/DL",      r"neural[- ]network|deep[- ]learning|\bDNN|\bCNN|\bMLP"),
    ("Evolutionary/swarm",     r"evolutionary|genetic|particle swarm|\bPSO\b|differential evolution|\bNSGA|swarm|annealing"),
    ("gm/ID / knowledge-based", r"gm/I[Dd]|knowledge[- ]based|design (?:equations|plan)|look[- ]?up table|\bLUT\b|precomputed"),
    ("Equation/convex",        r"geometric programming|convex|posynomial|equation[- ]based|analytical model"),
]
MOD_RX = [(n, re.compile(p, I)) for n, p in MOD_RULES]

APP_RULES = [    # the circuit
    ("Op-amp/OTA",        r"op[- ]?amps?|operational|\bOTAs?\b|amplifiers?(?! array)"),
    ("ADC/DAC",           r"\bADCs?\b|\bDACs?\b|data converters?|analog[- ]to[- ]digital|digital[- ]to[- ]analog|\bSAR\b|delta[- ]sigma|ΔΣ"),
    ("PLL/DLL/clocking",  r"\bPLLs?\b|\bDLLs?\b|\bVCOs?\b|oscillators?|\bTDCs?\b|clock"),
    ("Power/LDO",         r"\bLDOs?\b|regulators?|DC[-–]DC|power (?:converters?|management)|charge pumps?|buck|boost"),
    ("Comparator",        r"comparators?|sense amplifiers?|latch"),
    ("Reference/bias",    r"bandgap|voltage references?|current references?|bias"),
    ("RF",                r"\bRF\b|\bLNAs?\b|mixers?|power amplifiers?|\bPAs?\b|mm-?wave|antenna|matching network"),
    ("Filter",            r"active[- ]RC|\bGm[- ]?C\b|analog filters?|\bfilters?\b"),
    ("Memory",            r"\bSRAM\b|\bDRAM\b|\bNAND\b|flash|memory"),
    ("Wireline/SerDes",   r"serdes|wireline|transceivers?|\bCDR\b|equaliz"),
]
APP_RX = [(n, re.compile(p, I)) for n, p in APP_RULES]
CAL_RX = re.compile(r"silicon[- ](?:proven|verified|validated)|fabricated|measured|test[- ]?chip|prototype", I)


def _scan(rules, title, abstract, n=2):
    first = " ".join(re.split(r"(?<=[.!?])\s+", abstract or "")[:n])
    return [name for name, rx in rules if rx.search(title or "") or rx.search(first)]


def architectures(title, abstract):
    return _scan(ARCH_RX, title, abstract)


def modulations(title, abstract):
    return _scan(MOD_RX, title, abstract, 3)


def applications(title, abstract):
    return _scan(APP_RX, title, abstract)


def has_calibration(title, abstract):
    """Here: the result was demonstrated in silicon."""
    return bool(CAL_RX.search((title or "") + " " + (abstract or "")))


# ------------------------------------------------------------- spec parsing
NUM = r"(\d+(?:\.\d+)?)"
_SI = {"a": 1e-18, "f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "μ": 1e-6,
       "m": 1e-3, "": 1.0, "k": 1e3, "K": 1e3, "M": 1e6, "G": 1e9, "T": 1e12}
_X = r"\s*(?:×|x|X|times|-fold)"
SPEEDUP_RX = [re.compile(NUM + _X + r"\s*(?:faster|speed[- ]?ups?|acceleration|improvement in (?:runtime|speed|efficiency))", I),
              re.compile(r"speed[- ]?ups?\s*(?:of|by|up to|=|:)?\s*(?:up to\s*)?" + NUM + _X, I),
              re.compile(NUM + _X + r"\s*(?:fewer|less|reduction (?:in|of))\s*(?:\w+\s+){0,2}?(?:simulations?|SPICE|iterations|runtime|time|design time|samples)", I)]
NODE_NM_RX = re.compile(r"(?<![\w.])(\d{1,3})\s*-?\s*nm\b", I)
NODE_UM_RX = re.compile(r"(?<![\w.])(0\.\d{1,3})\s*-?\s*[µμu]m\b", I)
AREA_RX = re.compile(NUM + r"\s*-?\s*mm\s*(?:2|²|\^2)", I)
_FIXES = [(re.compile(r"(\d)\.\s(\d)"), r"\1.\2"), (re.compile(r"(\d)\s*-?\s*mu(m|W|A|V|s|J)\b"), r"\1 µ\2"),
          (re.compile(r"([µμ])\s+m\b"), r"\1m"), (re.compile(r"\\?hbox\s*"), "")]


def _norm(text):
    for rx, rep in _FIXES:
        text = rx.sub(rep, text)
    return text


def _neg(s):
    return -abs(float(re.sub(r"[−–\s-]", "", s)))


def _vals(rxs, text, conv, lo, hi):
    """Every plausible value (rounded to 3 significant digits for comparison)."""
    out = {}
    for rx in rxs:
        for m in rx.finditer(text or ""):
            try:
                v = conv(m)
            except (ValueError, KeyError):
                continue
            if v is not None and lo <= v <= hi:
                out.setdefault(float("%.3g" % v), v)
    return set(out.values())


def _pick(t, a, cands, best=max):
    """The title's value if it states one, else the abstract's only value; nothing when the abstract lists several."""
    vt, va = cands(t), cands(a)
    if vt:
        return best(vt)
    if len(va) == 1:
        return va.pop()
    return None


def parse_specs(title, abstract):
    """Speed-up over the baseline (x), process node (nm) and area (mm2): the title's value, or the abstract's
    only value; several different values leave the field empty."""
    t, a = _norm(title or ""), _norm(abstract or "")
    out = {}

    def put(k, v):
        if v is not None:
            out[k] = v
    put("speedup", _pick(t, a, lambda x: _vals(SPEEDUP_RX, x, lambda m: float(m.group(1)), 1.05, 1e6)))
    put("node", _pick(t, a, lambda x: _vals([NODE_NM_RX], x, lambda m: int(m.group(1)), 2, 500)
                      or _vals([NODE_UM_RX], x, lambda m: int(round(float(m.group(1)) * 1000)), 10, 1000)))
    put("area", _pick(t, a, lambda x: _vals([AREA_RX], x, lambda m: float(m.group(1)), 1e-4, 1e3)))
    return out


def spec_sources(title, abstract):
    """parse_specs() plus where each value came from: {"key": "t" | "a"}."""
    full = parse_specs(title, abstract)
    only_title = parse_specs(title, "")
    return full, {k: ("t" if only_title.get(k) == v else "a") for k, v in full.items()}


def derived(specs):
    return {}


# ------------------------------------------------------------- affiliations and dates (same rules as adc-census)
ORG_HINT = re.compile(r"universit|institut|college|school|KAIST|POSTECH|UNIST|DGIST|GIST|\bETH\b|EPFL|\bMIT\b|"
                      r"laborator|\blabs?\b|inc\b|ltd|corp|company|co\.|electronics|semiconductor|technolog|"
                      r"research|centre|center|academy|imec|tsmc|samsung|sk hynix|intel|mediatek|qualcomm|"
                      r"apple|google|huawei|broadcom|analog devices|texas instruments|nvidia|\bamd\b|\bibm\b|microsoft", I)


def org_and_country(aff):
    if not aff:
        return None, None
    parts = [p.strip() for p in aff.split(",") if p.strip()]
    if not parts:
        return None, None
    country = re.sub(r"\s+\d[\d\- ]*$", "", parts[-1])
    if re.fullmatch(r"(korea|south korea|republic of korea|korea \(south\))", country, I):
        country = "South Korea"
    elif re.fullmatch(r"(usa|u\.s\.a\.|united states|united states of america|us)", country, I):
        country = "USA"
    elif re.fullmatch(r"(prc|p\.r\. china|people's republic of china)", country, I):
        country = "China"
    org = None
    for p in parts:
        if ORG_HINT.search(p) and not re.match(r"(department|dept|school of|faculty|division)\b", p, I):
            org = p
            break
    if org is None:
        org = parts[1] if len(parts) > 2 else parts[0]
    if len(country) > 30 or re.search(r"\d", country):
        country = None
    return org, country


MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}


def parse_month(pubdate, year):
    s = (pubdate or "").lower()
    m = re.match(r"((?:19|20)\d{2})-(\d{2})", s)     # ISO dates from Crossref/OpenAlex
    if m:
        return "%s-%s" % m.groups()
    years = re.findall(r"(?:19|20)\d{2}", s)
    y = years[-1] if years else (str(year) if year else None)
    mon = None
    for tok in re.findall(r"[a-z]{3,}", s):
        if tok[:3] in MONTHS:
            mon = MONTHS[tok[:3]]
            break
    if y and mon:
        return "%s-%02d" % (y, mon)
    return y or ""
