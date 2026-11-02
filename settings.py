XLSX_PATH = "articles.xlsx"

SHEET_NAME = "articles_edited"
KEYWORDS_COUNTS_CSV = "output/keywords_counts.csv"
KEYWORDS_BY_ARTICLE_CSV = "output/keywords_por_artigo.csv"
RESULTS_DIR = "resultados_wordcloud/keywords_resultados"

SHEET_NAME_NO_SEARCH = "articles_string"
KEYWORDS_NO_SEARCH_COUNTS_CSV = "output/keywords_sem_busca_counts.csv"
KEYWORDS_NO_SEARCH_BY_ARTICLE_CSV = "output/keywords_sem_busca_por_artigo.csv"
RESULTS_NO_SEARCH_DIR = "resultados_wordcloud/keywords_sem_busca_resultados"

SHEET_NAME_ABSTRACT = "articles_abstract"
ABSTRACT_COUNTS_CSV = "output/abstract_counts.csv"
ABSTRACT_BY_ARTICLE_CSV = "output/abstract_por_artigo.csv"
RESULTS_ABSTRACT_DIR = "resultados_wordcloud/abstract_resultados"

SHEET_NAME_TITLE = "articles_abstract"
TITLE_COUNTS_CSV = "output/title_counts.csv"
TITLE_BY_ARTICLE_CSV = "output/title_por_artigo.csv"
RESULTS_TITLE_DIR = "resultados_wordcloud/title_resultados"

MASKS_DIR = "masks"
HELMET_MASK_PATH = "masks/helmet_mask.png"

ACRONYM_FIXES = {
    "Eeg": "EEG",
    "Hse": "HSE",
    "Hse Function": "HSE Function",
    "Hse Assurance Prescription Tool": "HSE Assurance Prescription Tool",
    "Ppe": "PPE",
    "Uav": "UAV",
    "Yolov7": "YOLOv7",
    "Openai Gpt": "OpenAI GPT",
    "Multimodal Ai": "Multimodal AI",
    "China'S Oil And Gas Sector": "China's Oil and Gas Sector",
}

MERGE_ALIASES = False

KEYWORD_ALIASES = {
    "Decision Support System": ["Decision Support Systems"],
    "Violation": ["Violations"],
    "Incident": ["Incident Data"],
    "Accident": ["Accidents"],
    "Hazard": ["Hazards"],
    "Real-Time": ["Real-Time Systems"],
}

SEARCH_TERMS = [
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Oil And Gas",
    "Upstream",
    "Safety",
    "Occupational",
    "HSE",
]

FIGURE = {
    "figsize_regular": (11, 6.0),
    "figsize_mask": (8.5, 9.5),
    "figsize_helmet": (8.5, 8.5),
    "dpi": 300,
    "output_formats": ["pdf", "png"],
    "font_family": "DejaVu Sans",
    "font_weight": "bold",
    "background_color": "white",
    "colormap": "Blues",
    "colormap_range": (0.48, 0.98), 
    "max_words_regular": 50,         
    "max_words_mask": 75,           
    "prefer_horizontal": 0.78,       
    "relative_scaling": 0.55,        
    "min_font_size": 11,
    "max_font_size_regular": 150,
    "max_font_size_mask": 130,
    "margin": 5,
    "random_state": 42,             
    "mask_contour_width": 1.8,
    "mask_contour_color": "#A6CEE4",
}
COMPOUND_TERMS = {
    "Oil And Gas": [
        "oil and gas",
        "oil & gas",
        "gas and oil",
        "gas & oil",
        "oil and gas industry",
        "petroleum industry",
        "petrochemical industry",
        "o&g",
    ],
    "Machine Learning": ["machine learning", "ml"],
    "Artificial Intelligence": ["artificial intelligence", "ai"],
    "Deep Learning": ["deep learning"],
    "Risk Management": ["risk management"],
    "Natural Language Processing": [
        "natural language processing",
        "natural language understanding",
        "nlp",
    ],
    "Data Mining": ["data mining"],
    "Big Data": ["big data"],
    "Drowsiness Detection": ["drowsiness detection"],
    "Human Reliability": ["human reliability"],
    "Hazard Identification": ["hazard identification"],
    "Decision Support": ["decision support system", "decision support systems", "decision support"],
    "Process Safety": ["process safety management", "process safety"],
    "Occupational Safety": ["occupational safety", "workplace safety", "industrial safety"],
    "Computer Vision": ["computer vision"],
    "Knowledge Graph": ["knowledge graphs", "knowledge graph"],
    "Neural Network": ["neural networks", "neural network"],
    "Bayesian Network": ["bayesian networks", "bayesian network"],
    "Standard Operating Procedures": ["standard operating procedures", "sops", "sop"],
    "PPE": [
        "personal protective equipment",
        "protective equipment",
        "ppe",
    ],
    "Helmet": ["safety helmet", "safety helmets", "hardhat", "hardhats", "helmet", "helmets"],
    "Real-Time": ["real-time", "real time"],
    "High-Risk": ["high-risk", "high risk"],
}

CUSTOM_STOPWORDS = {
    "paper", "study", "research", "article", "work", "present", "presented",
    "propose", "proposed", "proposes", "base", "based", "using", "use", "used",
    "utilize", "utilized", "method", "methods", "methodology", "approach",
    "approaches", "result", "results", "show", "shows", "shown", "demonstrate",
    "demonstrated", "demonstrates", "provide", "provides", "provided", "include",
    "includes", "including", "also", "however", "therefore", "thus", "furthermore",
    "moreover", "In", "in", "order", "various", "different", "new", "novel",
    "effective", "effectively", "significant", "significantly", "high", "low",
    "large", "small", "many", "several", "two", "three", "one", "first", "second",
    "can", "may", "must", "well", "such", "within", "across", "among", "due",
    "via", "per", "et", "al", "eg", "ie", "etc",
    "identify", "identified", "identifies", "subject", "subjects", "key", "area",
    "areas", "mean", "means", "develop", "developed", "developing", "main",
    "petronas", "assurance",
}
