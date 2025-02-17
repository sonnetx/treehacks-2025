# TreeHacks 2025: TreeTrash
https://devpost.com/software/treetrash

## Technical Overview
TreeTrash implements a multi-model, multi-modal AI pipeline for real-time waste analysis and environmental impact assessment. Our system architecture combines computer vision, large language models, and vector search capabilities to create a comprehensive waste management solution.

## Core Architecture

### Computer Vision Pipeline
- Primary Vision Model: Leveraged YOLOv8 for real-time object detection, fine-tuned on custom labeled dataset
- Frame Processing: Utilizes OpenCV for image preprocessing, including noise reduction and contrast enhancement
- Temporal Analysis: Implements a sliding window to track objects across multiple frames, enabling detection of newly added items

### AI Model Integration
- LLM: GPT-4o: for waste classification and initial analysis
- Secondary Models:
  - Perplexity AI for environmental impact research
  - GPT-4o-mini for structured data transformation and report generation
  - Gemini Pro as a VLM to post-process Vespa.ai RAG outputs
- Custom Prompt Engineering: Developed specialized prompts to improve classification accuracy

### RAG Implementation
- Vector Database: Vespa.ai for storing and retrieving sustainability documentation
- Embedding Model: ColPali (Efficient Document Retrieval with Vision Language Models)

## Data Pipeline
1. Image Capture & Processing
   - Resolution: 1920x1080 @ 30fps
   - Format: JPEG with quality preservation
   - Preprocessing: Gaussian blur (σ=1.5) for noise reduction

2. Object Detection & Classification
   - Model Architecture: YOLOv8 backbone with custom head
   - Inference Time: <50ms per frame
   - GPU Optimization: CUDA acceleration with TensorRT

3. Environmental Impact Analysis
   - Custom API integration with Perplexity
   - Structured output parsing using regex and NLP
   - Carbon footprint calculation using standardized metrics

4. Report Generation
   - Vector similarity search
   - Dynamic template generation
   - PDF export with visualizations

## Future Technical Enhancements

### LLM enhancements
- Improved prompting with DsPy for automated, bootstrapped prompt engineering
- Applying techniques like in-context learning

### RAG System Optimization
- Implementing hybrid search combining sparse and dense retrievers
- Adding cross-encoder reranking
- Developing custom embedding models for waste management domain

### Computer Vision Improvements
- Transfer learning from larger vision models
- Implementation of instance segmentation
- Real-time optical character recognition for packaging

### Robotic Integration
- ROS2 implementation for robotic arm control
- Computer vision-guided path planning
