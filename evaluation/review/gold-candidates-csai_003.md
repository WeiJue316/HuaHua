# 金标候选：csai_003

**问题**：What are reported limitations of chain-of-thought prompting on reasoning benchmarks?

　　→ 思维链提示在推理基准上被报告有哪些局限性？

**子问题**：

1. Which benchmarks expose limitations?
　　→ 哪些基准揭示了这些局限性？

2. Which failure modes are reported?
　　→ 报告了哪些失败模式？


**现有 gold**：2 篇　**年份范围**：(2022, 2026)　**引用图候选**：25 篇

## 判定标准

一篇论文算作 gold，当且仅当**领域专家会把它作为回答某个子问题的证据引用**。
按子问题分别判定，因为证据是按子问题分配的。

逐条检查：

1. 论文是否真正回答某个子问题（不是主题相邻）
2. 年份是否在声明范围内
3. 摘要是否包含可以作为证据的完整句子
4. 判定它支撑哪个子问题（填编号）

## 候选清单

| # | 年份 | 标题 | 中文标题(机翻) | DOI | 被引 | 关系 | 命中 | 判定 | 子问题 |
|---:|---:|---|---|---|---:|---|---:|---|---:|
| 1 | 2023 | The Art of SOCRATIC QUESTIONING: Recursive Thinking with Large Languag | 苏格拉底式提问的艺术：基于大语言模型的递归思维 | `10.18653/v1/2023.emnlp-main.255` | 24 | 引用了种子 | 4 | | |
| 2 | 2023 | Faithful Chain-of-Thought Reasoning | 忠实的思维链推理 | `10.18653/v1/2023.ijcnlp-main.20` | 111 | 引用了种子 | 3 | | |
| 3 | 2023 | On Second Thought, Let’s Not Think Step by Step! Bias and Toxicity in  | 再想想，还是别一步步推理了！零样本推理中的偏见与毒性 | `10.18653/v1/2023.acl-long.244` | 68 | 引用了种子 | 3 | | |
| 4 | 2023 | Can ChatGPT Defend its Belief in Truth? Evaluating LLM Reasoning via D | ChatGPT 能否为它对真理的信念辩护？通过辩论评估大语言模型推理 | `10.18653/v1/2023.findings-emnlp.795` | 47 | 引用了种子 | 2 | | |
| 5 | 2024 | From Automation to Augmentation: Redefining Engineering Design and Man | 从自动化到增强：在下一代人工智能时代重新定义工程设计与制造 | `10.21428/e4baedd9.e39b392d` | 22 | 引用了种子 | 2 | | |
| 6 | 2025 | Dual-process theory and decision-making in large language models | 双过程理论与大语言模型中的决策 | `10.1038/s44159-025-00506-1` | 11 | 引用了种子 | 2 | | |
| 7 | 2024 | Generative AI in the context of assistive technologies: Trends, limita | 辅助技术背景下的生成式人工智能：趋势、局限与未来方向 | `10.1016/j.imavis.2024.105347` | 45 | 引用了种子 | 1 | | |
| 8 | 2023 | Prompting is not a substitute for probability measurements in large la | 提示并非大语言模型中概率测量的替代品 | `10.18653/v1/2023.emnlp-main.306` | 37 | 引用了种子 | 1 | | |
| 9 | 2025 | “It’s Not Only Attention We Need”: Systematic Review of Large Language | “我们需要的不仅是注意力”：大语言模型在心理健康照护中的系统综述 | `10.2196/78410` | 20 | 引用了种子 | 1 | | |
| 10 | 2025 | Generating and leveraging explanations of AI/ML models in materials an | 在材料与制造研究中生成并利用人工智能/机器学习模型的解释 | `10.1016/j.patter.2025.101340` | 12 | 引用了种子 | 1 | | |
| 11 | 2024 | The Evaluation of GenAI Capabilities to Implement Professional Tasks | 生成式人工智能执行专业任务能力的评估 | `10.17323/2500-2597.2024.4.67.76` | 9 | 引用了种子 | 1 | | |
| 12 | 2025 | A Survey on Enhancing Causal Reasoning Ability of Large Language Model | 大语言模型因果推理能力增强研究综述 | `10.1007/978-981-96-8183-9_29` | 8 | 引用了种子 | 1 | | |
| 13 | 2025 | If You Give an LLM a Legal Practice Guide | 如果你给大语言模型一本法律实务指南 | `10.1145/3709025.3712220` | 5 | 引用了种子 | 1 | | |
| 14 | 2025 | Psychometrically derived 60-question benchmarks: Substantial efficienc | 基于心理测量学构建的60题基准：显著效率与人类—AI比较的可能性 | `10.1016/j.intell.2025.101922` | 4 | 引用了种子 | 1 | | |
| 15 | 2025 | Developing an Accounting Virtual Assistant Through Supervised Fine‐Tun | 通过小语言模型（SLM）的监督微调（SFT）开发会计虚拟助手 | `10.1002/isaf.70011` | 2 | 引用了种子 | 1 | | |
| 16 | 2025 | Comparative Evaluation of GPT Models in FHIR Proficiency | GPT模型在FHIR熟练度方面的比较评估 | `10.1145/3718095` | 2 | 引用了种子 | 1 | | |
| 17 | 2023 | Gender bias and stereotypes in Large Language Models | 大型语言模型中的性别偏见与刻板印象 | `10.1145/3582269.3615599` | 366 | 引用了种子 | 0 | | |
| 18 | 2024 | AI deception: A survey of examples, risks, and potential solutions | AI欺骗：实例、风险与潜在解决方案综述 | `10.1016/j.patter.2024.100988` | 219 | 引用了种子 | 0 | | |
| 19 | 2023 | Automated evaluation of written discourse coherence using GPT-4 | 使用GPT-4自动评估书面语篇连贯性 | `10.18653/v1/2023.bea-1.32` | 76 | 引用了种子 | 0 | | |
| 20 | 2025 | Sycophancy in Large Language Models: Causes and Mitigations | 大型语言模型中的谄媚现象：成因与缓解措施 | `10.1007/978-3-031-92611-2_5` | 76 | 引用了种子 | 0 | | |
| 21 | 2025 | Helpful, harmless, honest? Sociotechnical limits of AI alignment and s | 有益、无害、诚实？通过人类反馈强化学习实现人工智能对齐与安全的社会技术局限 | `10.1007/s10676-025-09837-2` | 46 | 引用了种子 | 0 | | |
| 22 | 2025 | Formal requirements engineering and large language models: A two-way r | 形式化需求工程与大语言模型：一条双向路线图 | `10.1016/j.infsof.2025.107697` | 46 | 引用了种子 | 0 | | |
| 23 | 2024 | Large language models can help boost food production, but be mindful o | 大语言模型有助于提升粮食生产，但需警惕其风险 | `10.3389/frai.2024.1326153` | 42 | 引用了种子 | 0 | | |
| 24 | 2024 | Quo Vadis ChatGPT? From large language models to Large Knowledge Model | ChatGPT何去何从？从大语言模型到大型知识模型 | `10.1016/j.compchemeng.2024.108895` | 41 | 引用了种子 | 0 | | |
| 25 | 2023 | Leveraging GPT-4 for Automatic Translation Post-Editing | 利用GPT-4进行自动翻译译后编辑 | `10.18653/v1/2023.findings-emnlp.804` | 40 | 引用了种子 | 0 | | |

## 摘要（判定用）

判据 3 要求确认摘要里存在可作为证据的完整句子，因此这里附上原文摘要。
机翻标题仅供快速定位，**判定必须依据英文原文**。

**1. The Art of SOCRATIC QUESTIONING: Recursive Thinking with Large Language Models**

- DOI：`10.18653/v1/2023.emnlp-main.255`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

Chain-of-Thought (CoT) prompting enables large language models to solve complex reasoning problems by generating intermediate steps.However, confined by its inherent singlepass and sequential generation process, CoT heavily relies on the initial decisions, causing errors in early steps to accumulate and impact the final answers.In contrast, humans adopt recursive thinking when tackling complex reasoning problems, i.e., iteratively breaking the original problem into approachable subproblems and aggregating their answers to resolve the original one.Inspired by the human cognitive process, we propose SOCRATIC QUESTIONING, a divide-and-conquer style algorithm that mimics the recursive thinking process.Specifically, SOCRATIC QUESTIONING leverages large language models to raise and answer sub-questions until collecting enough information to tackle the original question.Unlike CoT, SOCRATIC QUESTIONING explicitly navigates the thinking space, stimulates effective recursive thinking, and is more robust towards errors in the thinking process.Extensive experiments on several complex reasoning tasks, including MMLU, MATH, LogiQA, and visual question-answering demonstrate significant performance improvements over the stateof-the-art prompting methods, such as CoT, and Tree-of-Thought.The qualitative analysis clearly shows that the intermediate reasoning steps elicited by SOCRATIC QUESTIONING are similar to humans' recursively thinking process of complex reasoning problems 12 .

**2. Faithful Chain-of-Thought Reasoning**

- DOI：`10.18653/v1/2023.ijcnlp-main.20`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

Qing Lyu, Shreya Havaldar, Adam Stein, Li Zhang, Delip Rao, Eric Wong, Marianna Apidianaki, Chris Callison-Burch. Proceedings of the 13th International Joint Conference on Natural Language Processing and the 3rd Conference of the Asia-Pacific Chapter of the Association for Computational Linguistics (Volume 1: Long Papers). 2023.

**3. On Second Thought, Let’s Not Think Step by Step! Bias and Toxicity in Zero-Shot Reasoning**

- DOI：`10.18653/v1/2023.acl-long.244`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

Warning: This paper contains several toxic and offensive statements.Generating a Chain of Thought (CoT) has been shown to consistently improve large language model (LLM) performance on a wide range of NLP tasks.However, prior work has mainly focused on logical reasoning tasks (e.g.arithmetic, commonsense QA); it remains unclear whether improvements hold for more diverse types of reasoning, especially in socially situated contexts.Concretely, we perform a controlled evaluation of zero-shot CoT across two socially sensitive domains: harmful questions and stereotype benchmarks.We find that zeroshot CoT reasoning in sensitive domains significantly increases a model's likelihood to produce harmful or undesirable output, with trends holding across different prompt formats and model variants.Furthermore, we show that harmful CoTs increase with model size, but decrease with improved instruction following.Our work suggests that zero-shot CoT should be used with caution on socially important tasks, especially when marginalized groups or sensitive topics are involved.

**4. Can ChatGPT Defend its Belief in Truth? Evaluating LLM Reasoning via Debate**

- DOI：`10.18653/v1/2023.findings-emnlp.795`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

Large language models (LLMs) such as Chat-GPT and GPT-4 have shown impressive performance in complex reasoning tasks.However, it is difficult to know whether the models are reasoning based on deep understandings of truth and logic, or leveraging their memorized patterns in a relatively superficial way.In this work, we explore testing LLMs' reasoning by engaging with them in a debate-like conversation, where given a question, the LLM and the user need to discuss to make the correct decision starting from opposing arguments.Upon mitigating the Clever Hans effect, our task requires the LLM to not only achieve the correct answer on its own, but also be able to hold and defend its belief instead of blindly believing or getting misled by the user's (invalid) arguments and critiques, thus testing in greater depth whether the LLM grasps the essence of the reasoning required to solve the problem.Across a range of complex reasoning benchmarks spanning math, commonsense, logic and BIG-Bench tasks, we find that despite their impressive performance as reported in existing work on generating correct step-by-step solutions in the beginning, LLMs like ChatGPT cannot maintain their beliefs in truth for a significant portion of examples when challenged by oftentimes absurdly invalid arguments.Our work points to danger zones of model alignment, and also suggests more careful treatments and interpretations of the recent findings that LLMs can improve their responses based on feedback.1

**5. From Automation to Augmentation: Redefining Engineering Design and Manufacturing in the Age of NextGen-AI**

- DOI：`10.21428/e4baedd9.e39b392d`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

In the mid-2010s, as computing and other digital technologies matured (), researchers began to speculate about a new era of innovation—with artificial intelligence (AI) as the standard-bearer of a “Fourth Industrial Revolution” (). The release of generative AI (Gen-AI) technologies (e.g., ChatGPT) in late 2022 reignited the discussion, prompting us to wonder: what are the barriers, risks, and potential rewards to using gen-AI for design and manufacturing? As Gen-AI has entered the mainstream, geopolitics and business practices have shifted. Covid-19 disrupted global supply chains, tensions with import partners have risen, and military conflicts introduce new uncertainties. As companies consider propositions like ‘reshoring’ or ‘nearshoring/friendshoring’ production (), we recognize other hindrances: suboptimal resource allocation, labor market volatility and trends toward an older and geographically mismatched workforce, and highly concentrated tech markets that foster anticompetitive business practices. As the United States expands domestic production capacity (e.g., semiconductors and electric vehicles), Gen-AI could help us overcome those challenges. To investigate the current and potential usefulness of Gen-AI in design and manufacturing, we interviewed industry experts—including engineers, manufacturers, tech executives, and entrepreneurs. They have identified many opportunities for the deployment of Gen-AI: (1) reducing the incidence of costly late-stage design changes when scaling production; (2) providing information to designers and engineers, including identifying suitable design spaces and material formulations and incorporating consumer preferences; (3) improving test data interpretation to enable rapid validation and qualification; (4) democratizing workers’ access and usage of data to enable real-time insights and process adjustment; and (5) empowering less-skilled workers to be more productive and do more-expert work. Current Gen-AI solutions (e.g., ChatGPT, Claude) cannot accomplish these goals due to several key deficiencies, including the inability to provide robust, reliable, and replicable output; lack of relevant domain knowledge; unawareness of industry-standards requirements for product quality; failure to integrate seamlessly with existing workflow; and inability to simultaneously interpret data from different sources and formats. We propose a development framework for the next generation of Gen-AI tools for design and manufacturing (“NextGen-AI”): (1) provide better information about engineering tools, repositories, search methods, and other resources to augment the creative process of design; (2) integrate adherence to first principles when solving engineering problems; (3) leverage employees’ experiential knowledge to improve training and performance; (4) empower workers to perform new and more-expert productive tasks rather than pursue static automation of workers’ current functions; (5) create a collaborative and secure data ecosystem to train foundation models; and (6) ensure that new tools are safe and effective. These goals are extensive and will require broad-based buy-in from business leaders, operators, researchers, engineers, and policymakers. We recommend the following priorities to enable useful AI for design and manufacturing: (1) improve systems integration to ethically collect real-time data, (2) regulate data governance to ensure equal opportunity in development and ownership, (3) expand the collection of worker-safety data to assess industry-wide AI usage, (4) include engineers and operators in the development and uptake of new tools, and (5) focus on skills-complementary deployments to maximize productivity upside.

**6. Dual-process theory and decision-making in large language models**

- DOI：`10.1038/s44159-025-00506-1`
- 关联种子：`doi:10.48550/arxiv.2410.05229`（引用了种子）

Large language models (LLMs) are increasingly embedded in everyday decision-making scenarios, altering how people make choices. Despite the seemingly ‘superhuman’ capabilities of LLMs in some domains, there are pitfalls in the decision-making performance of LLMs and they should therefore be used with caution. In this Review, we examine LLM outputs through the lens of dual-process theory and against the backdrop of human decision-making. We detail how in decision-making scenarios, LLMs mimic both System-1-like responses — exhibiting cognitive biases and employing heuristics — and System-2-like responses — slow and carefully reasoned — through specific prompting methods. However, LLM reasoning is not fully analogous to human dual-process cognition. For instance, the ‘cognitive’ biases observed in LLMs often reflect patterns in their training data and LLMs exhibit specific non-human biases, such as hallucinations, that constrain their use in real-world decision-making. Despite these limitations, LLMs have the potential to augment human decision-making when deployed responsibly. Thus, we conclude with recommendations for mitigating biases and improving reliability to enable the deployment of LLMs as effective decision-support systems. The performance of large language models (LLMs) is often compared to human performance on decision-making tasks. In this Review, Brady and colleagues examine LLM outputs through the lens of dual-process theory, considering the hallmarks of System 1 and System 2 human decision-making.

**7. Generative AI in the context of assistive technologies: Trends, limitations and future directions**

- DOI：`10.1016/j.imavis.2024.105347`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

With the tremendous successes of Large Language Models (LLMs) like ChatGPT for text generation and Dall-E for high-quality image generation, generative Artificial Intelligence (AI) models have shown a hype in our society. Generative AI seamlessly delved into different aspects of society ranging from economy, education, legislation, computer science, finance, and even healthcare. This article provides a comprehensive survey on the increased and promising use of generative AI in assistive technologies benefiting different parties, ranging from the assistive system developers, medical practitioners, care workforce, to the people who need the care and the comfort. Ethical concerns, biases, lack of transparency, insufficient explainability, and limited trustworthiness are major challenges when using generative AI in assistive technologies, particularly in systems that impact people directly. Key future research directions to address these issues include creating standardized rules, establishing commonly accepted evaluation metrics and benchmarks for explainability and reasoning processes, and making further advancements in understanding and reducing bias and its potential harms. Beyond showing the current trends of applying generative AI in the scope of assistive technologies in four identified key domains, which include care sectors, medical sectors, helping people in need, and co-working, the survey also discusses the current limitations and provides promising future research directions to foster better integration of generative AI in assistive technologies. • Presenting the current trends in using generative AI in building assistive systems. • Highlighting the risks and benefits of using generative AI in assistive systems. • Discussing open issues and appealing future research directions.

**8. Prompting is not a substitute for probability measurements in large language models**

- DOI：`10.18653/v1/2023.emnlp-main.306`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

Prompting is now a dominant method for evaluating the linguistic knowledge of large language models (LLMs).While other methods directly read out models' probability distributions over strings, prompting requires models to access this internal information by processing linguistic input, thereby implicitly testing a new type of emergent ability: metalinguistic judgment.In this study, we compare metalinguistic prompting and direct probability measurements as ways of measuring models' linguistic knowledge.Broadly, we find that LLMs' metalinguistic judgments are inferior to quantities directly derived from representations.Furthermore, consistency gets worse as the prompt query diverges from direct measurements of next-word probabilities.Our findings suggest that negative results relying on metalinguistic prompts cannot be taken as conclusive evidence that an LLM lacks a particular linguistic generalization.Our results also highlight the value that is lost with the move to closed APIs where access to probability distributions is limited.

**9. “It’s Not Only Attention We Need”: Systematic Review of Large Language Models in Mental Health Care**

- DOI：`10.2196/78410`
- 关联种子：`doi:10.48550/arxiv.2410.05229`（引用了种子）

BACKGROUND: Mental health care systems worldwide face critical challenges, including limited access, shortages of clinicians, and stigma-related barriers. In parallel, large language models (LLMs) have emerged as powerful tools capable of supporting therapeutic processes through natural language understanding and generation. While previous research has explored their potential, a comprehensive review assessing how LLMs are integrated into mental health care, particularly beyond technical feasibility, is still lacking. OBJECTIVE: This systematic literature review investigates and conceptualizes the application of LLMs in mental health care by examining their technical implementation, design characteristics, and situational use across different touchpoints along the patient journey. It introduces a 3-layer morphological framework to structure and analyze how LLMs are applied, with the goal of informing future research and design for more effective mental health interventions. METHODS: A systematic literature review was conducted across PubMed, IEEE Xplore, JMIR, ACM, and AIS databases, yielding 807 studies. After multiple evaluation steps, 55 studies were included. These were categorized and analyzed based on the patient journey, design elements, and underlying model characteristics. RESULTS: Most studies assessed technical feasibility, whereas only a few examined the impact of LLMs on therapeutic outcomes. LLMs were used primarily for classification and text generation tasks, with limited evaluation of safety, hallucination risks, or reasoning capabilities. Design aspects, such as user roles, interaction modalities, and interface elements, were often underexplored, despite their significant influence on user experience. Furthermore, most applications focused on single-user contexts, overlooking opportunities for integrated care environments, such as artificial intelligence-blended therapy. The proposed 3-layer framework, which consists of the L1: LLM layer, L2: interface layer, and L3: situation layer, highlights critical design trade-offs and unmet needs in current research. CONCLUSIONS: LLMs hold promise for enhancing accessibility, personalization, and efficiency in mental health care. However, current implementations often overlook essential design and contextual factors that influence real-world adoption and outcomes. The review underscores that the self-attention mechanism, a key component of LLMs, alone is not sufficient. Future research must go beyond technical feasibility to explore integrated care models, user experience, and longitudinal treatment outcomes to responsibly embed LLMs into mental health care ecosystems.

**10. Generating and leveraging explanations of AI/ML models in materials and manufacturing research**

- DOI：`10.1016/j.patter.2025.101340`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

In some technical domains, machine learning (ML) tools, typically used with large datasets, must be adapted to small datasets, opaque design spaces, and expensive data generation. Specifically, generating data in many materials or manufacturing contexts can be expensive in time, materials, and expertise. Additionally, the "thought process" of complex "black box" ML models is often obscure to key stakeholders. This limitation can result in inefficient or dangerous predictions when errors in data processing or model training go unnoticed. Methods of generating human-interpretable explanations of complex models, called explainable artificial intelligence (XAI), can provide the insight needed to prevent these problems. In this review, we briefly present XAI methods and outline how XAI can also inform future behavior. These examples illustrate how XAI can improve manufacturing output, physical understanding, and feature engineering. We present guidance on using XAI in materials science and manufacturing research with the aid of demonstrative examples from literature.

**11. The Evaluation of GenAI Capabilities to Implement Professional Tasks**

- DOI：`10.17323/2500-2597.2024.4.67.76`
- 关联种子：`doi:10.48550/arxiv.2410.05229`（引用了种子）

Generative AI (GenAI) or large language models (LLMs) have been running the world since 2022, but despite all the trends surrounding the use of generative models, these cannot yet be used professionally. While they are most valued for ‘knowing everything’, nonetheless GenAI models cannot explain and prove. In this way we conceptualize the most recent problem of LLMs as the general trend of mistakes even in the core of knowledge and non-causality of mistake via the complexity of question, as the mistake can be named as an accident and be everywhere as the most limitation of professionalism. At their current stage of development, LLMs are not widely used in a professional context, nor have they replaced human workers. They do not event extend workers’ professional abilities.. These limitations of GenAI have one general: non-repayment. This article seeks to analyze GenAI’s professional viability by examining two models (GigaChatPro, GPT-4) in three fields of knowledge (economics, law, education) based on our unique Bloom’s taxonomy benchmark. To prove our assumption concerning the low possibility of its professional usage, we test three hypotheses: 1) the number of parameters of models have low elasticity regarding difficulty and taxonomy with even the right answer; 2) difficulty and taxonomy jointly have no effect on the correctness of an answer, 3) multiple choice is a factor that decreases the number of right answers of a model. We also present the results of GPT-4 and GigaChat MAX on our benchmark. Finally, we suggest what can be done about the limitations of GenAI’s architecture to reach at least a quasi-professional use.

**12. A Survey on Enhancing Causal Reasoning Ability of Large Language Models**

- DOI：`10.1007/978-981-96-8183-9_29`
- 关联种子：`doi:10.48550/arxiv.2410.05229`（引用了种子）

（源站未提供摘要——需另行获取，或直接放弃该候选）

**13. If You Give an LLM a Legal Practice Guide**

- DOI：`10.1145/3709025.3712220`
- 关联种子：`doi:10.48550/arxiv.2410.05229`（引用了种子）

Large language models struggle to answer legal questions that require applying detailed, jurisdiction-specific legal rules. Lawyers also find these types of question difficult to answer. For help, lawyers turn to legal practice guides: expert-written how-to manuals for practicing a type of law in a particular jurisdiction. Might large language models also benefit from consulting these practice guides? This article investigates whether providing LLMs with excerpts from these guides can improve their ability to answer legal questions. Our findings show that adding practice guide excerpts to LLMs' prompts tends to help LLMs answer legal questions. But even when a practice guide provides clear instructions on how to apply the law, LLMs often fail to correctly answer straightforward legal questions - questions that any lawyer would be expected to answer correctly if given the same information. Performance varies considerably and unpredictably across different language models and legal subject areas. Across our experiments' different legal domains, no single model consistently outperformed others. LLMs sometimes performed better when a legal question was broken down into separate subquestions for the model to answer over multiple prompts and responses. But sometimes breaking legal questions down resulted in much worse performance. These results suggest that retrieval augmented generation (RAG) will not be enough to overcome LLMs' shortcomings with applying detailed, jurisdiction-specific legal rules. Replicating our experiments on the recently released OpenAI o1 and o3-mini advanced reasoning models did not result in consistent performance improvements. These findings cast doubt on claims that LLMs will develop competency at legal reasoning tasks without dedicated effort directed toward this specific goal.

**14. Psychometrically derived 60-question benchmarks: Substantial efficiencies and the possibility of human-AI comparisons**

- DOI：`10.1016/j.intell.2025.101922`
- 关联种子：`doi:10.48550/arxiv.2410.05229`（引用了种子）

Large Language Model (LLM) benchmark evaluation tests often comprise thousands of questions. Based on psychometric principles, reliable and valid benchmark tests can likely be developed with as few as 60 items, comparable to human intelligence tests, which typically include only 15 to 60 items. The establishment of shorter benchmark tests offers numerous potential benefits, including more efficient evaluation of LLMs, the practical feasibility of creating parallel forms, and the ability to directly compare LLM performance with human capabilities. Consequently, we analysed the performance of 591 LLMs across three widely recognized benchmarks—HellaSwag, Winogrande, and GSM8K—and developed short-forms (≈ 60 questions each) using psychometric principles. The short-forms exhibited high internal consistency reliability, with coefficient omega values ranging from 0.96 for Winogrande to 0.99 for HellaSwag and GSM8K. Additionally, strong correlations between short- and long-form scores ( r ≈ 0.90) provided evidence of concurrent validity. Finally, model size (number of parameters) was a slightly stronger predictor of overall LLM performance for the short-forms compared to the long-forms, indicating that the short forms exhibited comparable, if not slightly superior, convergent validity. It is concluded that shorter benchmarks may accelerate AI development by enabling more efficient evaluations. Additionally, research into the nature of intelligence may be facilitated by benchmark short-forms by enabling direct comparisons between AI and human performance. • Applied psychometric principles to LLM test score evaluations. • First psychometric investigation of three prominent LLM benchmarks. • Reduced 1000+ question benchmarks to equally reliable/valid 60-item short-forms. • Achieved a 20× to 200× reduction in benchmark length without compromising accuracy. • Enabled feasible comparisons between AI systems and human performance.

**15. Developing an Accounting Virtual Assistant Through Supervised Fine‐Tuning (SFT) of a Small Language Model (SLM)**

- DOI：`10.1002/isaf.70011`
- 关联种子：`doi:10.48550/arxiv.2410.05229`（引用了种子）

ABSTRACT The development of an in‐house accounting bot—an artificial intelligence (AI) assistant capable of generating internally structured bookkeeping double‐entry posting schemes—is explored in this paper. The processes of curating a suitable dataset, selecting, and fine‐tuning a seven‐billion‐parameter language model, categorized as a small language model (SLM) (SLMs typically refer to models with fewer than 10 billion parameters, whereas medium‐sized models often have 14B parameters, and large‐scale models exceed 70B), are described. A human‐evaluated benchmark is also presented to assess model performance. To achieve efficient supervised fine‐tuning (SFT), low‐rank adaptation (LoRA) was employed, significantly reducing memory requirements by using a small set of trainable parameters while maintaining model expressiveness. The process of backpropagation was further optimized using Unsloth, a high‐performance training framework designed for efficient video memory usage and flash attention mechanisms, which accelerates adaptation and reduces memory overhead. The model whose layers were updated is called QwenCoder2.5. It was selected with the presumption that it would be able to learn how to generate and examine bookkeeping patterns generated by accounting information system (AIS) over a 17‐year history. This proof of concept aims to support researchers and practitioners exploring the integration of generative AI in accounting by providing insights into both the benefits and challenges of AI‐driven automation in bookkeeping tasks. The study demonstrates how an SLM can be fine‐tuned on a proprietary dataset of journal posting schemes to assist accountants, auditors, and financial analysts while also facilitating synthetic data generation. Challenges related to AI, data preprocessing, fine‐tuning optimization, and evaluation methodology are introduced and examined.

**16. Comparative Evaluation of GPT Models in FHIR Proficiency**

- DOI：`10.1145/3718095`
- 关联种子：`doi:10.48550/arxiv.2410.05229`（引用了种子）

Ensuring interoperability in healthcare data exchange is vital for advancing patient care, and Fast Healthcare Interoperability Resources (FHIR) has emerged as a cornerstone standard in this effort. As healthcare increasingly integrates AI for managing and interpreting complex data, proficiency in FHIR is essential to ensure seamless and reliable interactions with healthcare systems. This study evaluates the FHIR proficiency of Generative Pre-Trained Transformer (GPT) models, which serves as a critical benchmark for applying AI in healthcare. The performance of GPT-3.5, GPT-4.0, and two custom models was assessed in two FHIR examination scenarios using novel metrics, including Token Processing Cost (TPC), Accuracy-Adjusted Token Processing Cost (ATPC), Comprehensive Performance Index (CPI), and Quality-Adjusted Performance Score (QAPS). GPT-4.0 demonstrated superior accuracy and robustness, while custom models such as the “FHIR Interop Expert” showed strengths in domain-specific tasks through effective prompt engineering. Despite these capabilities, none of the models consistently achieved the \(\geq\) 99% accuracy required for high-stakes healthcare applications. The findings underscore the importance of refining domain-specific training and evaluation methods. The proposed metrics provide a replicable framework for assessing AI readiness, offering a foundation for the responsible and effective integration of AI into healthcare workflows.

**17. Gender bias and stereotypes in Large Language Models**

- DOI：`10.1145/3582269.3615599`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

Large Language Models (LLMs) have made substantial progress in the past several months, shattering state-of-the-art benchmarks in many domains. This paper investigates LLMs’ behavior with respect to gender stereotypes, a known issue for prior models. We use a simple paradigm to test the presence of gender bias, building on but differing from WinoBias, a commonly used gender bias dataset, which is likely to be included in the training data of current LLMs. We test four recently published LLMs and demonstrate that they express biased assumptions about men and women’s occupations. Our contributions in this paper are as follows: (a) LLMs are 3-6 times more likely to choose an occupation that stereotypically aligns with a person’s gender; (b) these choices align with people’s perceptions better than with the ground truth as reflected in official job statistics; (c) LLMs in fact amplify the bias beyond what is reflected in perceptions or the ground truth; (d) LLMs ignore crucial ambiguities in sentence structure 95% of the time in our study items, but when explicitly prompted, they recognize the ambiguity; (e) LLMs provide explanations for their choices that are factually inaccurate and likely obscure the true reason behind their predictions. That is, they provide rationalizations of their biased behavior. This highlights a key property of these models: LLMs are trained on imbalanced datasets; as such, even with the recent successes of reinforcement learning with human feedback, they tend to reflect those imbalances back at us. As with other types of societal biases, we suggest that LLMs must be carefully tested to ensure that they treat minoritized individuals and communities equitably.

**18. AI deception: A survey of examples, risks, and potential solutions**

- DOI：`10.1016/j.patter.2024.100988`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

This paper argues that a range of current AI systems have learned how to deceive humans. We define deception as the systematic inducement of false beliefs in the pursuit of some outcome other than the truth. We first survey empirical examples of AI deception, discussing both special-use AI systems (including Meta's CICERO) and general-purpose AI systems (including large language models). Next, we detail several risks from AI deception, such as fraud, election tampering, and losing control of AI. Finally, we outline several potential solutions: first, regulatory frameworks should subject AI systems that are capable of deception to robust risk-assessment requirements; second, policymakers should implement bot-or-not laws; and finally, policymakers should prioritize the funding of relevant research, including tools to detect AI deception and to make AI systems less deceptive. Policymakers, researchers, and the broader public should work proactively to prevent AI deception from destabilizing the shared foundations of our society.

**19. Automated evaluation of written discourse coherence using GPT-4**

- DOI：`10.18653/v1/2023.bea-1.32`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

The popularization of large language models (LLMs) such as OpenAI's GPT-3 and GPT-4 have led to numerous innovations in the field of AI in education.With respect to automated writing evaluation (AWE), LLMs have reduced challenges associated with assessing writing quality characteristics that are difficult to identify automatically, such as discourse coherence.In addition, LLMs can provide rationales for their evaluations (ratings) which increases score interpretability and transparency.This paper investigates one approach to producing ratings by training GPT-4 to assess discourse coherence in a manner consistent with expert human raters.The findings of the study suggest that GPT-4 has strong potential to produce discourse coherence ratings that are comparable to human ratings, accompanied by clear rationales.Furthermore, the GPT-4 ratings outperform traditional NLP coherence metrics with respect to agreement with human ratings.These results have implications for advancing AWE technology for learning and assessment.

**20. Sycophancy in Large Language Models: Causes and Mitigations**

- DOI：`10.1007/978-3-031-92611-2_5`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

（源站未提供摘要——需另行获取，或直接放弃该候选）

**21. Helpful, harmless, honest? Sociotechnical limits of AI alignment and safety through Reinforcement Learning from Human Feedback**

- DOI：`10.1007/s10676-025-09837-2`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

This paper critically evaluates the attempts to align Artificial Intelligence (AI) systems, especially Large Language Models (LLMs), with human values and intentions through Reinforcement Learning from Feedback methods, involving either human feedback (RLHF) or AI feedback (RLAIF). Specifically, we show the shortcomings of the broadly pursued alignment goals of honesty, harmlessness, and helpfulness. Through a multidisciplinary sociotechnical critique, we examine both the theoretical underpinnings and practical implementations of RLHF techniques, revealing significant limitations in their approach to capturing the complexities of human ethics, and contributing to AI safety. We highlight tensions inherent in the goals of RLHF, as captured in the HHH principle (helpful, harmless and honest). In addition, we discuss ethically-relevant issues that tend to be neglected in discussions about alignment and RLHF, among which the trade-offs between user-friendliness and deception, flexibility and interpretability, and system safety. We offer an alternative vision for AI safety and ethics which positions RLHF approaches within a broader context of comprehensive design across institutions, processes and technological systems, and suggest the establishment of AI safety as a sociotechnical discipline that is open to the normative and political dimensions of artificial intelligence.

**22. Formal requirements engineering and large language models: A two-way roadmap**

- DOI：`10.1016/j.infsof.2025.107697`
- 关联种子：`doi:10.48550/arxiv.2410.05229`（引用了种子）

Large Language Models (LLMs) have made remarkable advancements in emulating human linguistic capabilities, showing potential also in executing various requirements engineering (RE) tasks. However, despite their generally good performance, the adoption of LLM-generated solutions and artefacts prompts concerns about their correctness, fairness, and trustworthiness. This paper aims to address the concerns associated with the use of LLMs in RE activities. Specifically, it seeks to develop a roadmap that leverages formal methods (FMs) to provide guarantees of correctness, fairness, and trustworthiness when LLMs are utilised in RE. Symmetrically, it aims to explore how LLMs can be employed to make FMs more accessible. We use two sets of examples to show the current limits of FMs when used in software development and of LLMs when used for RE tasks. The highlighted limitations are addressed by proposing two roadmaps grounded in the current literature and technologies. The proposed examples show the potential and limits of FMs in supporting software development and of LLMs when used for RE tasks. The initial investigation into how these limitations can be overcome has been concretised in two detailed roadmaps for the RE and, more largely, the software engineering community. The proposed roadmaps offer a promising approach to address the concerns of correctness, fairness, and trustworthiness associated with the use of LLMs in RE tasks through the use of FMs and to enhance the accessibility of FMs by utilising LLMs. • We exemplify the use of formal methods in software development • We outline a roadmap to increase usability of formal methods with the support of LLMs • We show how LLMs can be support requirements engineers in automating manual tasks • We propose a roadmap for the use of formal techniques to make LLMs reliable

**23. Large language models can help boost food production, but be mindful of their risks**

- DOI：`10.3389/frai.2024.1326153`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

Coverage of ChatGPT-style large language models (LLMs) in the media has focused on their eye-catching achievements, including solving advanced mathematical problems and reaching expert proficiency in medical examinations. But the gradual adoption of LLMs in agriculture, an industry which touches every human life, has received much less public scrutiny. In this short perspective, we examine risks and opportunities related to more widespread adoption of language models in food production systems. While LLMs can potentially enhance agricultural efficiency, drive innovation, and inform better policies, challenges like agricultural misinformation, collection of vast amounts of farmer data, and threats to agricultural jobs are important concerns. The rapid evolution of the LLM landscape underscores the need for agricultural policymakers to think carefully about frameworks and guidelines that ensure the responsible use of LLMs in food production before these technologies become so ingrained that policy intervention becomes challenging.

**24. Quo Vadis ChatGPT? From large language models to Large Knowledge Models**

- DOI：`10.1016/j.compchemeng.2024.108895`
- 关联种子：`doi:10.48550/arxiv.2410.05229`（引用了种子）

The startling success of ChatGPT and other large language models (LLMs) using transformer-based generative neural network architecture in applications such as natural language processing and image synthesis has many researchers excited about potential opportunities in process systems engineering (PSE). The almost human-like performance of LLMs in these areas is indeed very impressive, surprising, and a major breakthrough. Their capabilities are very useful in certain tasks, such as writing first drafts of documents, code writing assistance, text summarization, etc. However, their success is limited in highly scientific domains as they cannot yet reason, plan, or explain due to their lack of in-depth mechanistic domain knowledge. This is a problem in domains such as chemical engineering as they are governed by fundamental laws of physics and chemistry (and biology), constitutive relations, and highly technical knowledge about materials, processes, and systems. Although purely data-driven machine learning has its immediate uses, the long-term success of AI in scientific and engineering domains would depend on developing hybrid AI systems that combine first principles and technical knowledge effectively. We call these hybrid AI systems Large Knowledge Models (LKMs), as they will not be limited to only NLP-based techniques or NLP-like applications. In this paper, we discuss the challenges and opportunities in developing such systems in chemical engineering. • Historical perspective on large language models. • Deficiencies of LLMs in scientific and engineering domains. • The importance of symbolic AI and domain knowledge. • Large knowledge models (LKMs) as the future.

**25. Leveraging GPT-4 for Automatic Translation Post-Editing**

- DOI：`10.18653/v1/2023.findings-emnlp.804`
- 关联种子：`doi:10.48550/arxiv.2305.04388`（引用了种子）

While Neural Machine Translation (NMT) represents the leading approach to Machine Translation (MT), the outputs of NMT models still require translation post-editing to rectify errors and enhance quality under critical settings.In this work, we formalize the task of direct translation post-editing with Large Language Models (LLMs) and explore the use of GPT-4 to automatically post-edit NMT outputs across several language pairs.Our results demonstrate that GPT-4 is adept at translation post-editing, producing meaningful and trustworthy edits to translations that help improve its general quality as well as remove different classes of major errors in translations.In particular, human evaluations on assessing edit trustworthiness show that GPT-4 exhibits a large improvement over the prior state-of-the-art LLM.Notably, we improve upon state-of-the-art performance on WMT-22 English-Chinese, English-German, Chinese-English and German-English language pairs using GPT-4 based post-editing, as evaluated by state-of-the-art MT quality metrics.However, we also show that GPT-4 could produce hallucinated edits, thereby urging caution in its use as an expert translation post-editor. LimitationsWe proposed a formalization to study direct automatic post-editing with state-of-the-art LLMs and investigated a number of research questions through this formalization.However, we only have API-level access to GPT-4.Even though we conducted our experiments on WMT-22 test sets and system outputs, the curation of which falls outside the cut-off date for GPT-4 training data; due to only black-box access to the model, we cannot rule out the possibility of data contamination, even on the WMT-22 test sets.


## 记录

| 字段 | 内容 |
|---|---|
| 复核人 | |
| 日期 | |
| 采纳的候选编号 | |
| 候选来源说明 | 引用图扩展（OpenAlex citations / references） |
