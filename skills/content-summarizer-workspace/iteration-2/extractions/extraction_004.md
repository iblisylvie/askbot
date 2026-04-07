# Extraction 004 - Chunk 4

## Key Points
1. **革命性论文的定义与意义**: 讲述者定义了"革命性论文"的概念——那些能让研究收敛曲线出现断崖式下降(drop)的工作，如ResNet、Transformer、GPT-3、CLIP等，这些论文彻底改变了渐进式的研究路径。

2. **对LLM终将凋零的预言**: 讲述者认为LLM(大语言模型)终将凋零(They won't die, they just fade away)，LLM是很好的工具但不是构建通用智能系统的基石，不是世界模型的地基。

3. **凯明的领导力与方法论**: 详细描述了凯明(Kaiming He)作为研究领导者的特质——单枪匹马承担80-90%的一作+通讯作者职责，重视基础设施建设(TPU、检测框架)，以及通过Excel表格进行实验管理的独特方法论。

4. **自监督学习的起伏历程**: 从MOCO(V1/V2/V3)到MAE的探索历程，经历了"大起"(自监督学习在视觉任务上取得突破)到"大落"(发现无法scale up)，但证明了表征学习是普世方法论。

5. **研究基础设施的重要性**: "工欲善其事，必先利其器"——研究的上限取决于基础设施的好坏，在弱的baseline上的提升可能只是灌水，只有在强的baseline上的突破才是真正的ground breaking。

## Key Quotes (EXACT, with speaker)
1. **讲述者**: "我觉得LLM终将凋零...不对不对，LLM永远不会死，但终将凋零...老兵不死，终将凋零...就是说这个东西一定会有它的价值，它是一个很好的工具，我现在会天天使用LLM，但它不是我们构建一个通用智能系统的基石。"

2. **讲述者**: "我觉得凯明也真的show出来这个leadership，就是说他真的承担了八九十%的一作加这个last author就是默做这种corresponding通讯作者的职责。他需要自己写code，需要自己跑很多很多的实验，需要最后把paper写完去想这个story去present。"

3. **讲述者**: "凯明教我的一件事情是说，你的research的上限其实取决于你基础设施的好坏。如果你的baseline很差的话，你可能很容易自欺欺人，你是做不出来什么东西的。"

## Entities Mentioned

### People
- **凯明(Kaiming He)**: 讲述者的导师/合作者，ResNet作者，以单枪匹马的研究风格和卓越领导力著称，喜欢做individual contributor而非manager，本科物理背景，喜欢进化生物学和哲学
- **ROSS**: 与凯明、吴雨欣一起搭建检测基础设施的研究者
- **吴雨欣**: 现在在KIMI，参与搭建检测框架基础设施
- **翔宇**: 之前与讲述者聊过自监督学习无法scale up的原因

### Organizations
- **FAIR (Facebook AI Research)**: 讲述者待了4年的实验室
- **Google**: 提供TPU云服务
- **KIMI**: 吴雨欣目前所在的公司

### Concepts
- **Diffusion Model/DDPM**: 生成模型
- **ResNet**: 凯明的代表作，深度残差网络
- **AlexNet**: 深度学习里程碑工作
- **ImageNet**: 计算机视觉基准数据集
- **RCNN/Fast R-CNN/Mask R-CNN**: 目标检测系列工作
- **Transformer / Attention Is All You Need**: NLP领域的革命性架构
- **GPT-3 / BERT / CLIP / ViT**: 大模型系列工作
- **NeRF / Gaussian Splatting**: 3D视觉领域革命性工作
- **Contrastive Learning (对比学习)**: 自监督学习方法，MOCO系列
- **MAE (Masked Autoencoder)**: 掩码自编码器，另一种自监督学习路径
- **MOCO (Momentum Contrast)**: 对比学习系列工作，有V1/V2/V3版本
- **Point Contrast**: 3D点云上的自监督学习工作
- **TPU**: Google的AI加速器芯片
- **Linear Probing / Fine-tuning**: 表征学习的两种评估方式
- **Individual Contributor (IC)**: 个人贡献者角色

### Books/Resources
- 无明确提及具体书籍

## Personal Journey Elements

### Background
- **在FAIR的4年经历**: 这是讲述者研究生涯的重要阶段，经历了从探索期到产出期再到新的探索期的循环
- **与凯明共事的经历**: 这段合作深刻塑造了讲述者对研究的理解和方法论

### Relationships
- **凯明作为导师的影响**: 
  - 不仅是学术指导，更是方法论和思维方式的传承
  - 通过Excel表格教讲述者如何管理实验、如何获得梯度信号
  - 让讲述者感受到"只要在他身边，我就觉得自己变聪明了"
  - 一起打游戏(魔兽世界、炉石传说)建立的非正式关系

### Turning Points
- **MOCO系列的成功与局限**: 最初以为找到了自监督学习的答案，但后来发现无法scale up
- **MAE的尝试**: 转向更简单的自编码器路径，取得了好结果但仍无法scale up
- **对LLM的重新定位**: 从追逐热点到认识到LLM不是通用智能的终极答案

### Personal Stories
- **Excel表格作为"第一课"**: FAIR实习生进来第一课是学习用Excel表格追踪实验，这个看似"文职"的工作实际上蕴含深刻的研究方法论
- **与凯明打游戏的经历**: "前一个小时讨论research，后一个小时讨论游戏"，凯明天梯爬得比讲述者高，"各个维度上被碾压"
- **TPU基础设施的搭建**: 凯明单枪匹马在TPU上build一整套infrastructure，支撑了MOCO、MAE、DiT等系列工作

## Intellectual Framework

### Methodology
- **"革命性论文"的判断标准**: 能让研究收敛曲线出现断崖式下降(drop)的工作
- **实验管理的Excel方法论**:
  - 精细设计表格：关注哪些metric、记录哪些内容
  - 控制实验数量：既不能做太少(信号不明确)，也不能瞎跑所有实验
  - 对照式对比：实验之间要有关系，形成梯度信号
  - 最大化信息增益(Maximizing information)：负面结果的反方向就是正向信号
  - 预测实验结果：在跑实验前先预测，验证自己的思维链条
- **基础设施优先**: "工欲善其事，必先利其器"——研究上限取决于基础设施的好坏

### Philosophy
- **对LLM的看法**: LLM是工具但不是通用智能的基石，终将凋零(They won't die, they just fade away)
- **对研究突破的理解**: 真正的breakthrough不是在弱的baseline上的提升，而是在强的baseline上的突破
- **对代表作的追求**: 希望自己的研究能成为改变领域方向的"革命性论文"

### Influences
- **凯明的研究哲学**: 单枪匹马深入一线、重视基础设施、追求真正的突破而非灌水
- **进化生物学**: 凯明最喜欢聊的话题，可能影响了他对研究的理解
- **物理和量子力学**: 凯明的本科背景

### Evolution
- **从追逐热点到追求本质**: 从MOCO/MAE的探索中认识到scale up的重要性
- **从执行者到思考者**: 从单纯做实验到思考实验设计背后的方法论
- **对AI发展路径的重新理解**: 从认为自监督学习是答案，到认识到还有很长的路要走

## Questions Raised
- **下一个革命在哪里**: LLM之后，什么技术能带来真正的通用智能？
- **为什么对比学习无法scale up**: 这是未解答的核心问题，翔宇和讲述者讨论过但本段未展开
- **自监督学习的未来**: MAE和对比学习都无法scale up，那么视觉自监督学习的正确路径是什么？
- **如何参与下一次革命**: 讲述者希望不是创造impact，而是通过个人经历、合作模式、认知思考来影响AI发展

## Connections
- **与前文(chunk_003)的关联**: 前文可能讨论了研究历程的早期阶段，本段深入讲述了在FAIR的具体经历和凯明的影响
- **与后文(chunk_005)的关联**: 后文可能会继续展开"世界模型"的讨论，以及讲述者离开FAIR后的新探索
- **与整个访谈的关联**: 本段是讲述者研究方法论的核心阐述，为理解他后续的职业选择和研究方向提供了关键背景
