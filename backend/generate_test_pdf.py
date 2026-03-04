"""
Generate a sample PDF document for testing PageIndex POC.
Creates a multi-page document about AI/ML with a clear table of contents.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "test_documents", "ai_technology_report.pdf")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=letter,
    topMargin=1 * inch,
    bottomMargin=0.75 * inch,
    leftMargin=1 * inch,
    rightMargin=1 * inch,
    title="Artificial Intelligence & Machine Learning: A Comprehensive Report 2025",
    author="PageIndex POC Team",
)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    "CustomTitle",
    parent=styles["Title"],
    fontSize=24,
    spaceAfter=30,
    textColor=HexColor("#1a202c"),
    alignment=TA_CENTER,
)

h1_style = ParagraphStyle(
    "H1",
    parent=styles["Heading1"],
    fontSize=18,
    spaceBefore=20,
    spaceAfter=12,
    textColor=HexColor("#2563eb"),
)

h2_style = ParagraphStyle(
    "H2",
    parent=styles["Heading2"],
    fontSize=14,
    spaceBefore=14,
    spaceAfter=8,
    textColor=HexColor("#1a202c"),
)

body_style = ParagraphStyle(
    "CustomBody",
    parent=styles["Normal"],
    fontSize=11,
    leading=16,
    spaceAfter=10,
    textColor=HexColor("#4a5568"),
)

toc_style = ParagraphStyle(
    "TOCEntry",
    parent=styles["Normal"],
    fontSize=12,
    leading=20,
    textColor=HexColor("#2563eb"),
)

story = []

# ─── Title Page ───────────────────────────────────────────────────────
story.append(Spacer(1, 2 * inch))
story.append(Paragraph(
    "Artificial Intelligence &<br/>Machine Learning",
    title_style
))
story.append(Spacer(1, 0.3 * inch))
story.append(Paragraph(
    "A Comprehensive Technology Report — 2025 Edition",
    ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=14,
                   alignment=TA_CENTER, textColor=HexColor("#718096"))
))
story.append(Spacer(1, 1 * inch))
story.append(Paragraph(
    "Prepared by: Technology Research Division<br/>"
    "Published: March 2025<br/>"
    "Classification: Internal Use",
    ParagraphStyle("Meta", parent=styles["Normal"], fontSize=10,
                   alignment=TA_CENTER, textColor=HexColor("#a0aec0"))
))
story.append(PageBreak())

# ─── Table of Contents ────────────────────────────────────────────────
story.append(Paragraph("Table of Contents", h1_style))
story.append(Spacer(1, 0.3 * inch))

toc_entries = [
    ("1. Executive Summary", "3"),
    ("2. Introduction to Artificial Intelligence", "4"),
    ("   2.1 History and Evolution", "4"),
    ("   2.2 Current State of AI", "5"),
    ("3. Machine Learning Fundamentals", "6"),
    ("   3.1 Supervised Learning", "6"),
    ("   3.2 Unsupervised Learning", "7"),
    ("   3.3 Reinforcement Learning", "7"),
    ("4. Deep Learning and Neural Networks", "8"),
    ("   4.1 Convolutional Neural Networks (CNNs)", "8"),
    ("   4.2 Recurrent Neural Networks (RNNs)", "9"),
    ("   4.3 Transformers and Attention Mechanisms", "9"),
    ("5. Large Language Models (LLMs)", "10"),
    ("   5.1 Architecture and Training", "10"),
    ("   5.2 GPT, Claude, and Gemini", "11"),
    ("   5.3 Applications and Limitations", "11"),
    ("6. AI in Industry", "12"),
    ("   6.1 Healthcare", "12"),
    ("   6.2 Finance", "13"),
    ("   6.3 Manufacturing", "13"),
    ("7. Ethical Considerations", "14"),
    ("8. Future Outlook and Conclusions", "15"),
]

for entry, page in toc_entries:
    dots = "." * (60 - len(entry))
    story.append(Paragraph(f"{entry} {dots} {page}", toc_style))

story.append(PageBreak())

# ─── Section 1: Executive Summary ─────────────────────────────────────
story.append(Paragraph("1. Executive Summary", h1_style))
story.append(Paragraph(
    "Artificial Intelligence (AI) has emerged as the most transformative technology of the 21st century. "
    "This report provides a comprehensive analysis of AI and Machine Learning technologies as of 2025, "
    "covering fundamental concepts, recent breakthroughs, industrial applications, and future projections.",
    body_style
))
story.append(Paragraph(
    "Key findings include: (1) Large Language Models have achieved human-level performance on numerous "
    "benchmark tasks; (2) AI adoption in enterprise settings has grown 340% since 2020; (3) The global "
    "AI market is projected to reach $1.8 trillion by 2030; (4) Retrieval-Augmented Generation (RAG) "
    "has become the standard architecture for enterprise knowledge systems.",
    body_style
))
story.append(Paragraph(
    "The report identifies three critical trends: the shift from vector-based to reasoning-based retrieval "
    "systems, the emergence of agentic AI workflows, and the growing importance of AI safety and alignment. "
    "Organizations that fail to adopt AI strategies risk significant competitive disadvantage.",
    body_style
))
story.append(Paragraph(
    "Total investment in AI research and development globally exceeded $180 billion in 2024, with the "
    "United States, China, and the European Union leading in both funding and talent development. "
    "The healthcare sector saw the largest growth in AI adoption, followed by financial services and manufacturing.",
    body_style
))
story.append(PageBreak())

# ─── Section 2: Introduction to AI ────────────────────────────────────
story.append(Paragraph("2. Introduction to Artificial Intelligence", h1_style))

story.append(Paragraph("2.1 History and Evolution", h2_style))
story.append(Paragraph(
    "The concept of artificial intelligence dates back to the 1950s, when Alan Turing posed the fundamental "
    "question 'Can machines think?' in his seminal 1950 paper. The Dartmouth Conference of 1956 is widely "
    "considered the birthplace of AI as an academic discipline, bringing together researchers who believed "
    "that 'every aspect of learning or any other feature of intelligence can in principle be so precisely "
    "described that a machine can be made to simulate it.'",
    body_style
))
story.append(Paragraph(
    "Early AI research focused on symbolic approaches and expert systems, which dominated the field through "
    "the 1970s and 1980s. The 'AI winters' of the 1970s and late 1980s saw reduced funding and interest "
    "as the limitations of symbolic AI became apparent. The resurgence began in the 1990s with the advent "
    "of statistical machine learning methods and increased computational power.",
    body_style
))
story.append(Paragraph(
    "The modern era of AI, beginning around 2012, has been characterized by the deep learning revolution. "
    "AlexNet's victory in the ImageNet competition marked a watershed moment, demonstrating that deep neural "
    "networks could dramatically outperform traditional computer vision methods. Since then, advances in "
    "hardware, data availability, and algorithmic innovations have accelerated progress exponentially.",
    body_style
))
story.append(PageBreak())

story.append(Paragraph("2.2 Current State of AI", h2_style))
story.append(Paragraph(
    "As of 2025, AI systems can understand and generate human language, create realistic images and videos, "
    "write code, analyze complex scientific data, and even assist in drug discovery. The capabilities of "
    "modern AI systems would have been considered science fiction just a decade ago.",
    body_style
))
story.append(Paragraph(
    "Key milestones achieved in recent years include: GPT-4's performance on standardized exams exceeding "
    "the 90th percentile of human test-takers; AlphaFold's prediction of protein structures for virtually "
    "all known proteins; autonomous vehicles achieving Level 4 certification in multiple jurisdictions; "
    "and AI systems passing the Turing test in controlled settings.",
    body_style
))
story.append(Paragraph(
    "The current AI landscape is characterized by rapid commercialization, with thousands of startups and "
    "major technology companies competing to develop and deploy AI solutions. The technology has moved "
    "from research labs to production systems, powering everything from search engines and recommendation "
    "systems to medical diagnostics and financial trading algorithms.",
    body_style
))
story.append(PageBreak())

# ─── Section 3: ML Fundamentals ──────────────────────────────────────
story.append(Paragraph("3. Machine Learning Fundamentals", h1_style))
story.append(Paragraph(
    "Machine Learning (ML) is a subset of AI that enables systems to learn and improve from experience "
    "without being explicitly programmed. ML algorithms build mathematical models from training data to "
    "make predictions or decisions. The three primary paradigms of machine learning are supervised learning, "
    "unsupervised learning, and reinforcement learning.",
    body_style
))

story.append(Paragraph("3.1 Supervised Learning", h2_style))
story.append(Paragraph(
    "Supervised learning involves training models on labeled datasets where the correct output is known. "
    "The algorithm learns to map inputs to outputs by finding patterns in the training data. Common "
    "applications include image classification, spam detection, medical diagnosis, and price prediction.",
    body_style
))
story.append(Paragraph(
    "Popular supervised learning algorithms include: Linear and Logistic Regression for simple predictive "
    "tasks; Decision Trees and Random Forests for complex non-linear relationships; Support Vector Machines "
    "for classification in high-dimensional spaces; and Neural Networks for learning hierarchical representations. "
    "The choice of algorithm depends on the nature of the data, the size of the dataset, and the complexity "
    "of the underlying relationships.",
    body_style
))
story.append(PageBreak())

story.append(Paragraph("3.2 Unsupervised Learning", h2_style))
story.append(Paragraph(
    "Unsupervised learning works with unlabeled data, seeking to discover hidden patterns or structures. "
    "Common techniques include clustering (K-means, DBSCAN, hierarchical clustering), dimensionality "
    "reduction (PCA, t-SNE, UMAP), and generative models (VAEs, GANs). These methods are particularly "
    "valuable for exploratory data analysis, anomaly detection, and customer segmentation.",
    body_style
))

story.append(Paragraph("3.3 Reinforcement Learning", h2_style))
story.append(Paragraph(
    "Reinforcement Learning (RL) trains agents to make sequences of decisions by maximizing cumulative "
    "reward signals. The agent interacts with an environment, observes states, takes actions, and receives "
    "rewards. Notable achievements include AlphaGo defeating the world champion in Go, OpenAI Five beating "
    "professional Dota 2 teams, and robotic systems learning complex manipulation tasks.",
    body_style
))
story.append(Paragraph(
    "Modern RL approaches include Deep Q-Networks (DQN), Proximal Policy Optimization (PPO), and "
    "model-based methods. The field has seen growing interest in offline RL, multi-agent RL, and "
    "applications in real-world robotics and autonomous driving. Reward shaping and sim-to-real transfer "
    "remain active research areas.",
    body_style
))
story.append(PageBreak())

# ─── Section 4: Deep Learning ────────────────────────────────────────
story.append(Paragraph("4. Deep Learning and Neural Networks", h1_style))
story.append(Paragraph(
    "Deep learning uses multi-layered neural networks to learn representations of data at increasing "
    "levels of abstraction. The 'deep' in deep learning refers to the number of layers in the network. "
    "Modern deep learning architectures can contain hundreds of billions of parameters and require "
    "massive computational resources for training.",
    body_style
))

story.append(Paragraph("4.1 Convolutional Neural Networks (CNNs)", h2_style))
story.append(Paragraph(
    "CNNs revolutionized computer vision by automatically learning spatial hierarchies of features. "
    "Key components include convolutional layers for feature extraction, pooling layers for spatial "
    "reduction, and fully connected layers for classification. Architectures like ResNet, EfficientNet, "
    "and Vision Transformers (ViT) have pushed state-of-the-art performance across image tasks. "
    "CNNs have found applications beyond vision, including audio processing, time-series analysis, "
    "and natural language processing. The total number of parameters in modern CNNs can range from "
    "millions (MobileNet) to billions (large ViT models).",
    body_style
))
story.append(PageBreak())

story.append(Paragraph("4.2 Recurrent Neural Networks (RNNs)", h2_style))
story.append(Paragraph(
    "RNNs are designed for sequential data, maintaining hidden states that capture information from "
    "previous time steps. Long Short-Term Memory (LSTM) and Gated Recurrent Unit (GRU) networks "
    "addressed the vanishing gradient problem, enabling learning of long-range dependencies. "
    "While largely superseded by Transformers for NLP tasks, RNNs remain relevant for real-time "
    "sequential processing and resource-constrained environments.",
    body_style
))

story.append(Paragraph("4.3 Transformers and Attention Mechanisms", h2_style))
story.append(Paragraph(
    "The Transformer architecture, introduced in 'Attention Is All You Need' (Vaswani et al., 2017), "
    "has revolutionized machine learning. Self-attention mechanisms allow the model to weigh the "
    "importance of different parts of the input, enabling parallel processing and better capture of "
    "long-range dependencies. Transformers form the backbone of virtually all modern language models "
    "and have been successfully adapted for vision (ViT), audio (Whisper), and multi-modal tasks.",
    body_style
))
story.append(Paragraph(
    "Key innovations in transformer architectures include multi-head attention, which allows the model "
    "to attend to information from different representation subspaces; positional encodings, which "
    "inject sequence order information; and layer normalization, which stabilizes training. "
    "Recent advances include mixture-of-experts (MoE) architectures, flash attention for efficient "
    "computation, and various approaches to extend context length beyond initial training limits.",
    body_style
))
story.append(PageBreak())

# ─── Section 5: LLMs ─────────────────────────────────────────────────
story.append(Paragraph("5. Large Language Models (LLMs)", h1_style))

story.append(Paragraph("5.1 Architecture and Training", h2_style))
story.append(Paragraph(
    "Large Language Models are transformer-based models trained on massive text corpora using "
    "self-supervised learning objectives, primarily next-token prediction. Training involves two "
    "main phases: pre-training on large-scale web data (costing millions of dollars in compute) "
    "and fine-tuning with human feedback (RLHF/DPO) to align model outputs with human preferences.",
    body_style
))
story.append(Paragraph(
    "The scaling laws discovered by Kaplan et al. (2020) demonstrated that model performance improves "
    "predictably with increases in model size, dataset size, and compute budget. This finding drove "
    "the development of increasingly large models, from GPT-2 (1.5B parameters) to GPT-4 (estimated "
    "1.7T parameters in a mixture-of-experts configuration). Training a frontier LLM in 2025 requires "
    "approximately 10,000-30,000 GPUs running for several months.",
    body_style
))
story.append(PageBreak())

story.append(Paragraph("5.2 GPT, Claude, and Gemini", h2_style))
story.append(Paragraph(
    "The major LLM families include OpenAI's GPT series, Anthropic's Claude, Google's Gemini, and "
    "Meta's Llama (open-source). GPT-4 and its successors have demonstrated remarkable capabilities "
    "in reasoning, coding, and creative tasks. Claude has differentiated itself with enhanced safety "
    "features and longer context windows (up to 200K tokens). Gemini uniquely integrates multi-modal "
    "understanding from inception. Llama 3 has made high-quality LLMs accessible through open-source "
    "release, enabling organizations to self-host and fine-tune models for specific domains.",
    body_style
))

story.append(Paragraph("5.3 Applications and Limitations", h2_style))
story.append(Paragraph(
    "LLM applications span code generation (GitHub Copilot, Cursor), content creation, customer service "
    "automation, legal document analysis, and scientific research assistance. Retrieval-Augmented "
    "Generation (RAG) has emerged as the dominant paradigm for grounding LLM outputs in factual data.",
    body_style
))
story.append(Paragraph(
    "Important limitations include: hallucination (generating plausible but false information); "
    "limited reasoning on novel problems; high computational costs; potential for bias amplification; "
    "and challenges in maintaining factual accuracy. Traditional vector-based RAG systems attempt to "
    "address hallucination but suffer from retrieval accuracy issues — similarity does not equal "
    "relevance. Novel approaches like PageIndex use reasoning-based retrieval to overcome these limitations.",
    body_style
))
story.append(PageBreak())

# ─── Section 6: AI in Industry ───────────────────────────────────────
story.append(Paragraph("6. AI in Industry", h1_style))

story.append(Paragraph("6.1 Healthcare", h2_style))
story.append(Paragraph(
    "AI is transforming healthcare through improved diagnostics, drug discovery, and personalized medicine. "
    "Deep learning models can detect cancers in medical images with accuracy matching or exceeding "
    "radiologists. AlphaFold has predicted structures of over 200 million proteins, accelerating drug "
    "discovery timelines from years to months. AI-powered clinical decision support systems are helping "
    "physicians make more accurate diagnoses and treatment recommendations. The global AI in healthcare "
    "market reached $28 billion in 2024 and is projected to grow to $150 billion by 2030.",
    body_style
))
story.append(PageBreak())

story.append(Paragraph("6.2 Finance", h2_style))
story.append(Paragraph(
    "Financial institutions use AI for algorithmic trading, fraud detection, credit scoring, and risk "
    "assessment. Natural language processing enables automated analysis of earnings reports, regulatory "
    "filings, and market sentiment. AI-powered chatbots handle over 60% of routine customer inquiries "
    "at major banks. Quantitative hedge funds using AI-driven strategies have outperformed traditional "
    "funds by an average of 8% annually over the past five years. The total investment in AI by the "
    "financial services industry exceeded $35 billion in 2024.",
    body_style
))

story.append(Paragraph("6.3 Manufacturing", h2_style))
story.append(Paragraph(
    "AI-driven predictive maintenance reduces unplanned downtime by up to 50%. Computer vision systems "
    "perform quality inspection at speeds and accuracy levels impossible for human inspectors. Digital "
    "twins powered by AI simulate manufacturing processes, enabling optimization before physical "
    "implementation. The Industry 4.0 transformation has seen AI integrated across supply chain "
    "management, production planning, and logistics optimization. Smart factories utilizing AI have "
    "reported average productivity improvements of 20-30% and defect reduction rates of up to 90%.",
    body_style
))
story.append(PageBreak())

# ─── Section 7: Ethics ───────────────────────────────────────────────
story.append(Paragraph("7. Ethical Considerations", h1_style))
story.append(Paragraph(
    "As AI systems become more capable and pervasive, ethical considerations have moved to the forefront. "
    "Key concerns include algorithmic bias, privacy implications, job displacement, autonomous weapons, "
    "and the concentration of AI capabilities in a few large organizations.",
    body_style
))
story.append(Paragraph(
    "Regulatory frameworks are emerging globally: the EU AI Act provides a risk-based classification "
    "system; the US has issued executive orders on AI safety; and China has enacted regulations on "
    "generative AI and deepfakes. The concept of 'responsible AI' encompasses fairness, accountability, "
    "transparency, and safety (FATS). Organizations are increasingly establishing AI ethics boards "
    "and implementing responsible AI frameworks to guide development and deployment decisions.",
    body_style
))
story.append(Paragraph(
    "AI safety research has gained significant attention, with organizations like Anthropic, OpenAI, "
    "and DeepMind dedicating substantial resources to alignment research. The goal is to ensure that "
    "AI systems behave in accordance with human values and intentions, especially as systems become "
    "more capable. Constitutional AI, reward modeling, and interpretability research are key approaches "
    "being pursued to address these challenges.",
    body_style
))
story.append(PageBreak())

# ─── Section 8: Future Outlook ───────────────────────────────────────
story.append(Paragraph("8. Future Outlook and Conclusions", h1_style))
story.append(Paragraph(
    "The next five years will likely see: (1) Artificial General Intelligence (AGI) becoming a serious "
    "research target rather than a distant aspiration; (2) AI agents capable of autonomous multi-step "
    "task completion; (3) Widespread adoption of reasoning-based AI systems; (4) Significant advances "
    "in AI efficiency, enabling powerful models on consumer hardware.",
    body_style
))
story.append(Paragraph(
    "The shift from vector-based to reasoning-based retrieval represents a fundamental paradigm change. "
    "Systems like PageIndex demonstrate that LLM-powered tree search can achieve 98.7% accuracy on "
    "financial benchmarks, significantly outperforming traditional vector-based RAG. This approach — "
    "using hierarchical document indexes and reasoning-based navigation — more closely mirrors how "
    "human experts analyze complex documents.",
    body_style
))
story.append(Paragraph(
    "In conclusion, AI and Machine Learning technologies are advancing at an unprecedented pace. "
    "Organizations must invest in AI capabilities while carefully managing risks. The convergence of "
    "more capable models, better retrieval systems, and agentic AI workflows will create transformative "
    "opportunities across every industry. The key differentiator will be the ability to deploy AI "
    "systems that are not only powerful but also reliable, safe, and aligned with organizational values.",
    body_style
))

# Market data table
story.append(Spacer(1, 0.3 * inch))
story.append(Paragraph("AI Market Projections ($ Billions)", h2_style))

table_data = [
    ["Sector", "2023", "2024", "2025 (Est.)", "2030 (Proj.)"],
    ["Healthcare", "$15B", "$28B", "$42B", "$150B"],
    ["Finance", "$22B", "$35B", "$48B", "$120B"],
    ["Manufacturing", "$12B", "$19B", "$28B", "$90B"],
    ["Retail", "$8B", "$14B", "$22B", "$75B"],
    ["Total Global", "$150B", "$230B", "$340B", "$1,800B"],
]

table = Table(table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2563eb")),
    ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f7fafc")]),
    ("PADDING", (0, 0), (-1, -1), 8),
]))
story.append(table)

# Build PDF
doc.build(story)
print(f"✅ PDF created: {OUTPUT_PATH}")
print(f"   File size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")
