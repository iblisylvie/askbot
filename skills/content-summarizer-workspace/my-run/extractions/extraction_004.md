# Chunk 4 Extraction

## Key Points
- [ ] 讨论AI领域里程碑式论文的意义：这些论文（如ResNet、Transformer、GPT-3、BERT、CLIP、ViT等）彻底改变了渐进式研究的方向，带来研究曲线的断崖式下降（drop），推动领域进入新阶段
- [ ] 凯明（Kaiming He）的研究方法论：强调基础设施（infrastructure/scaffolding）的重要性，研究上限取决于baseline的质量，必须将baseline做到极致才能做出真正的突破
- [ ] 自监督学习（Self-supervised Learning）的探索历程：从MOCO（对比学习）到MAE（Masked Autoencoder），虽然取得好结果但未能像LLM那样scale up，最终未能实现预期的突破
- [ ] 实验设计与追踪的方法论：使用Excel表格精细追踪实验，关注实验间的对照关系，学会从负面结果中提取信号，做实验前要先预测结果以验证思维链条
- [ ] TPU基础设施的建设：凯明单枪匹马在TPU上搭建整套基础设施，支撑了MOCO、MAE、DiT等一系列工作，体现"工欲善其事，必先利其器"的理念

## Key Quotes
- "这些工作的意义在于，大家本来是渐进式的通向一个方向，突然有这样的一个论文横空出世，彻底改变了我们刚刚说这个stock caic gradient design的过程，所以你看他的收敛的曲线有一个drop" (受访者)
- "你的research的上限其实取决于你baseline的好坏。如果你的baseline很差的话，你可能很容易自欺欺人，你是做不出来什么东西的" (受访者转述凯明的观点)
- "一个negative的信号的反方向就是一个正向的信号，一个positive结果的正方向也是一个好的信号" (受访者)

## Entities Mentioned
- People: 
  - 凯明（Kaiming He）: 主导MOCO、MAE、DiT等项目，强调基础设施建设和高质量baseline的研究方法论
  - 吴雨欣: 参与搭建detection基础设施，现就职于KIMI
  - Ross: 参与detection相关工作
  - 翔宇: 曾讨论过自监督学习无法scale up的原因
- Organizations: 
  - FAIR（Facebook AI Research）实验室
  - Google Cloud（提供TPU资源）
  - KIMI（吴雨欣现就职公司）
- Concepts: 
  - ResNet、AlexNet、ImageNet、R-CNN/Faster R-CNN
  - Transformer、BERT、GPT-3、CLIP、ViT（Vision Transformer）
  - Diffusion Model、DDPM、Nerf、Gaussian Splatting
  - MOCO（对比学习）、MAE（Masked Autoencoder）
  - Self-supervised Learning、Contrastive Learning、Representation Learning
  - TPU、Infrastructure/Scaffolding、Baseline
  - Linear Probing、Fine-tuning
  - Individual Contributor (IC)

## Questions Raised
- 为什么自监督学习（MOCO、MAE等）无法像LLM那样scale up？
- LLM是否终将凋零？受访者认为LLM不会死但终将fade away，不是构建通用智能系统的基石
- 下一个AI领域的革命（revolution）会是什么？会在什么时候出现？
- 如何设计实验才能最大化信息量（Maximizing information）？
- 什么样的论文才能真正称得上"代表作"，对领域产生根本性改变？

## Connections
- 前序话题: 前一段讨论了AI领域代表性工作的标准和意义，以及什么样的工作能真正改变领域发展方向
- 后续可能话题: 
  - 在FAIR实验室后续的研究探索（DiT等工作）
  - 对世界模型（World Model）的讨论
  - 当前研究探索期的迷茫与未来可能的方向
  - 凯明的个人特质和领导力风格
