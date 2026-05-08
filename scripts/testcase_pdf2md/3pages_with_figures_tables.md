# Agentic AI for Personalized Physiotherapy: A Multi-Agent Framework for Generative Video Training and Real-Time Pose Correction

Abhishek Dharmaratnakar, Srivaths Ranganathan, Anushree Sinha, Debanshu Das Google,Mountain View, USA Email: {dharmaratnakar, srivaths, sinhaanushree, debanshu} @google.com

Abstract-At-home physiotherapy compliance remains critically low due to a lack of personalized supervision and dynamic feedback.Existing digital health solutions rely on static,prerecorded video libraries or generic 3D avatars that fail to account fora patient's specific injury limitations or home environment. In this paper, we_ propose a novel Multi-Agent System (MAS) architecture that leverages Generative AI and computer vision to close the tele-rehabilitation loop.Our framework consists of four specialized micro-agents:a Clinical Extraction Agent that parses unstructured medical notes into kinematic constraints; a Video Synthesis Agent that utilizes foundational video generation models to create personalized, patient-specific exercise videos；a Vision Processing Agent for real-time pose estimation; and a Diagnostic Feedback Agent that issues corrective instructions. We present the system architecture, detail the prototype pipeline using Large Language Models and MediaPipe,and outline our clinical evaluation plan.This work demonstrates the feasibility of combining generative media with agentic autonomous decisionmaking to scale personalized patient care safely and effectively.

IndexTerms-GenerativeAI, Multi-AgentSystems, Telemedicine,Physiotherapy,Computer Vision,Digital Health, Explainable AI

# I. INTRODUCTION

Decentralizing physical rehabilitation to the home is paramount for scaling global healthcare. However，selfdirected at-home physiotherapy is plagued by chronically low compliance rates and high instances of incorrect exercise execution [1]. Traditional tele-rehabilitation platforms predominantly offer static video tutorials or asynchronous monitoring. These conventional systems lack the semantic intelligence required to provide real-time,personalized feedback,leaving patients vulnerable to secondary injuries and suboptimal recovery trajectories.

While sensory platforms and virtual coaching systems [2] have attempted to bridge this gap,they often rely on cumbersome hardware or rigid,hard-coded rule engines.The advent of Agentic Artificial Intelligence (Agentic AI) offers a transformative paradigm. Unlike passive machine learning pipelines,Agentic AI utilizes autonomous micro-agents that plan, execute,and collaborate to solve complex reasoning tasks dynamically.

This paper introduces a Multi-Agent System (MAS) specifically architected for personalized physiotherapy. Our core contribution is an end-to-end framework that translates unstructured clinical prescriptions into a continuous,real-time feedback loop.It dynamically generates hyper-personalized training videos respecting biomechanical limits and utilizes real-time computer vision to enforce those limits during patient execution.

# II. RELATED WORK

# A.Computer Vision and Pose Estimation in Digital Health

Recent studies demonstrate the efficacy of markerless pose estimation algorithms,such as MediaPipe and YOLO-Pose, for the real-time assessment of physiotherapy movements [4], [5].While contemporary Vision-Language Models (VLMs) demonstrate broad capabilities,recent evaluations indicate they struggle with fine-grained spatio-temporal tracking required for stroke and injury rehabilitation [6]. This limitation necessitates our hybrid approach: delegating spatial tracking to specialized vision models and high-level reasoning to Large Language Models (LLMs).

# B. Generative Al and Video Synthesis

Generative AI is rapidly reshaping physical health management.Early applications utilized Generative Adversarial Networks (GANs) to synthesize missing motion data for rehabilitation classification [7]. Currently, diffusion models and foundational video transformers enable high-fidelity biomedical video synthesis [8]. While the generation of synthetic humans (deepfakes） introduces ethical considerations,its application in physical health allows for the creation of tailored virtual avatars that can safely demonstrate tactical and physical movements [9].Our system utilizes this capability to synthesize digital “physio-twins” tailored to the patient's precise injury constraints.

# C.Explainable AI (XAI) in Precision Medicine

Clinical applications of AI require strict transparency. The integration of Explainable AI (XAI) in digital health is critical to fostering trust among both clinicians and patients [3]. In our architecture,XAI is inherently built into the Diagnostic Feedback Agent,which maps detected kinematic deviations directly back to the original physician's explicit constraints, ensuring all automated guidance is clinically interpretable.

# III. MULTI-AGENT SYSTEM ARCHITECTURE

Our MAS architecture acts as a localized, intelligent loop between the clinician and the patient.It comprises four distinct micro-agents that communicate via a unified, shared state object (Patient State).

![](images/f8815ae066593668a608793fdd95a23e21ffa2491e317920ec0aac3a52d48114.jpg)  
Figure 1．The proposed pipeline orchestration demonstrating the cyclic handoff between different agents

# Algorithm 1 Multi-Agent Pipeline for Real-Time Physiotherapy Assessment

Require: Unstructured clinical prescription $N _ { r x }$ , Continuous RGB camera frames $F _ { t }$   
Ensure: Continuous real-time corrective feedback $C _ { t }$   
1: Initialize Shared State: $S \gets \{ \mathrm { n o t e s } : N _ { r x }$ ,constraints : $\emptyset , \mathsf { p o s e } : \emptyset$ ,feedback:0}   
2:Initialize Agents: Clinical Extraction $\left( A _ { C l i n } \right)$ , Video Synthesis $( A _ { V i d } )$ ,Vision Processing $( A _ { V i s } )$   
3:{Phase 1: Pre-Session Extraction & Synthesis}   
4: S.constraints $ A _ { C l i n }$ .Process(S.notes)   
5:S.video_u $\mathfrak { w }  A _ { V i d }$ .Process(S.constraints)   
6: {Phase 2: Real-Time Diagnostic Feedback Loop}   
7: Let $\theta _ { t a r g e t }  S$ .constraints[max_angle]   
8:Let $\delta \gets 5 ^ { \circ }$ {Acceptable error margin}   
9: while rehabilitation session is active do   
10: Capture instantaneous frame $F _ { t }$   
11: $S . { \mathsf { p o s e } } \gets A _ { V i s }$ .Process $\left( F _ { t } \right)$   
12: $\theta _ { c u r r e n t } $ Extract target joint angle from S.pose   
13: if $\theta _ { c u r r e n t } > ( \theta _ { t a r g e t } + \delta )$ then   
14: $C _ { t } \gets$ “Warning: Arm is too high. Lower to avoid strain."   
15: else if $\theta _ { c u r r e n t } < ( \theta _ { t a r g e t } - \delta )$ then   
16: $C _ { t } \gets$ “Raise your arm slightly higher.”   
17: else   
18: $C _ { t } \gets$ “Perfect form.Hold."   
19: end if   
20: S.feedback $ C _ { t }$   
21: Output: $C _ { t }$ to patient via audio/text interface   
22:end while

# A. Clinical Extraction Agent

The pipeline is initiated by the Clinical Extraction Agent. This agent processes unstructured text such as post-operative notes or physio prescriptions and translates them into a standardized JSON schema. Table I illustrates the mapping of clinical free-text into the structured boundaries that govern the entire system's safety protocols.

Table ICLINICAL EXTRACTION: TEXT TO CONSTRAINT MAPPING  

<table><tr><td>Unstructured Clinical Note</td><td>Extracted JSON Constraint</td></tr><tr><td>“Patient recovering from rotator cuff tear.Max 9O deg shoulder abduc- tion.”</td><td>{ joint:&quot;shoulder&quot;, axis:&quot;abduction&quot;, max_angle:90，urgency: &quot;high&quot;}</td></tr><tr><td>“Ensure knee does not track past the toes during squats.Go slow.&quot;</td><td>{joint:&quot;knee&quot;, spatial_rel: &quot;behind_toe&quot;, max_velocity:0.5}</td></tr></table>

# B. Video Synthesis Agent

Generic exercise videos are dangerous for patients with limited range of motion (ROM). The Video Synthesis Agent takes the JSON constraints and constructs a highly specific generative prompt. For instance,it prompts the foundational video model to generate a virtual avatar performing a shoulder abduction that explicitly stops at $8 9 ^ { \circ }$ . This provides the patient with a visually accurate target that does not encourage overextension.

# C. Vision Processing Agent

Running locally to preserve patient privacy， the Vision Processing Agent utilizes lightweight pose estimation models [4].It isolates key anatomical landmarks (e.g.，acromion, lateral epicondyle,ulnar styloid） to calculate instantaneous joint angles. This agent operates at $\geq 3 0$ frames per second (FPS) to ensure kinematic data is captured without latency.

# D. Diagnostic Feedback Agent

The Diagnostic Feedback Agent represents the “virtual coach.’ It continuously evaluates the output of the Vision Agent against the Clinical Agent's constraints.As outlined in Table II, it employs a hybrid deterministic-generative approach to deliver feedback that is both safe and empathetic.

# IV. SYSTEM IMPLEMENTATION AND ORCHESTRATION

To validate the conceptual architecture,we developed a prototype pipeline in Python.The system state is maintained dynamically, simulating continuous handoffs between the autonomous agents.

The core orchestration logic, directly reflecting our system design，ensures strict state management. The deterministic rules applied in the diagnostic feedback algorithm ensure that LLM hallucinations cannot override hard physiological safety limits.

Table IIDIAGNOSTIC FEEDBACK DECISION MATRIX  

<table><tr><td>Kinematic State</td><td>Condition</td><td>Generated Action</td><td>Feedback</td></tr><tr><td>Acurrent &gt; Amax +5°</td><td>Critical Violation</td><td>Stop. Immediate ing issued:“Arm is too high．Lower toavoid</td><td>warn-</td></tr><tr><td>Amax -10°≤A≤Amax</td><td>Optimal Zone</td><td>strain.” Praise.“Perfect form. Hold this position.”</td><td></td></tr><tr><td>Acurrent &lt;Amax -15°</td><td>Under-extension</td><td>Encourage.“Raise your armslightly higher if</td><td></td></tr><tr><td>Vcurrent &gt;Vsafe_limit</td><td>High Velocity</td><td>comfortable.” Pace.“Slow down your movement to maintain control.&quot;</td><td></td></tr></table>

![](images/a31b65751570b5f90e0f091879ac9bba15b8820e0b4c08cc1481c852c1d1a569.jpg)  
Figure 2.Example of the generated patient interface:The Video Synthesis Agent creates a personalized“physio-twin”demonstrator.

# V.PRELIMINARY EVALUATION AND FUTURE WORK

While this work represents an architectural framework, preliminary bench-testing of the underlying components estimates promising metrics (Table III).The latency of the Vision Processing Agent (utilizing MediaPipe) is estimated to be well within the acceptable bounds for real-time human-computer interaction $( < 5 0 ~ \mathrm { m s } )$ .

# VI. CONCLUSION

This paper introduced a novel Multi-Agent framework designed to solve the critical challenges of at-home physiotherapy. By combining the semantic reasoning of Large Language Models to extract explicit clinical constraints,the generative capabilities of modern video synthesis to create customized demonstrations,and the precision of real-time computer vision,our system establishes a closed-loop,intelligent rehabilitation environment.

# VII. ACKNOWLEDGEMENTS

The Authors acknowledge the use of AI for refining text and images.

# REFERENCES

[1]A.K. Triantafyllidis and A. Tsanas,“Applications of Machine Learning in Real-Life Digital Health Interventions:Review of the Literature,” Journal of Medical Internet Research,vol.21,no.4,p.el2286,Apr. 2019.   
[2]V.D.Tsakanikas et al.,“Evaluating the Performance of Balance Physiotherapy Exercises Using a Sensory Platform:The Basis fora Persuasive Balance Rehabilitation Virtual Coaching System,”Frontiers in Digital Health,vol.2,Nov.2020.   
[3] B.Allen,“The Promise of Explainable AI in Digital Health for Precision Medicine:ASystematic Review,Journal of Personalized Medicine,vol. 14,no.277,2024.   
[4]V.Garcia and O.C. Santos,“Towards Intelligent Assessment in Personalized Physiotherapy with Computer Vision,”Sensors,vol.25,no.3436, 2025.   
[5] F.M.da Silva Luz,“Enhancing Virtual Physiotherapy Through Computer Vision and Pose Estimation,”Master's thesis,ISCTE-Instituto Universitario de Lisboa,2024.   
[6] V.Li et al.,“The Potential and Limitations of Vision-Language Models for Human Motion Understanding:A Case Study in Data-Driven Stroke Rehabilitation,”arXiv preprint arXiv:2511.17727vl,2025.   
[7] L.Li and A.Vakanski,“Generative Adversarial Networks for Generation and Classification of Physical Rehabilitation Movement Episodes,” International Journal of Machine Learning and Computing,vol.8,no. 5,pp.428-436,Oct.2018.   
[8] N.Algethami,T. Iqbal,and I. Ullah,“Generative AI for biomedical video synthesis:a review,”Artificial Intelligence Review,vol.58,no. 392,Oct. 2025.   
[9]T.Fan and M.M.Moghimi,“A Review of Deepfake Technology in Physical Health Management and Application,”International Journal of Intelligent Systems,2026.

Table III PRELIMINARY SYSTEM COMPONENT ESTIMATED METRICS   

<table><tr><td>Component Metric</td><td>Estimated Value</td><td>Target Threshold</td></tr><tr><td>Pose Estimation Latency</td><td>28 ms</td><td>&lt;50 ms</td></tr><tr><td>Joint Angle Error Margin</td><td>±3.2°</td><td>&lt;5°</td></tr><tr><td>Clinical Text Parsing Acc.</td><td>96.5%</td><td>&gt; 95%</td></tr><tr><td>Video Synthesis Generation</td><td>45 sec</td><td>&lt; 60 sec</td></tr></table>

The primary challenge remains the Video Synthesis Agent. Ensuring absolute temporal consistency and anatomical accuracy in synthesized videos requires further refinement of diffusion models [8].

Future work entails deploying this MAS in a full-scale clinical trial to evaluate joint-angle tracking accuracy against wearable inertial measurement units (IMUs).