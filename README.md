# Automatic Receipt Recognition

Camera-based receipt image processing is a specialised area within document image understanding, presenting more significant challenges than traditional document image processing due to its capture in real-life scenarios. The goal is to evaluate the performance of various image processing models on receipt photos, focusing on the effectiveness of different models and algorithms on synthetic and real data, and discussing the impact of different data on the experimental results. Furthermore, it seeks to construct a feasible solution for practical application.

The experimental approach involves object detection models such as NanoDet with ShuffleNet as the backbone and SSD with MobileNet as the backbone. The research combines the output of the object detection model with pre-trained PaddleOCR-based text detection models like DB and EAST, as well as the text recognition model CRNN. It applies transfer learning to compare their performance in a specific receipt scenario. 

Additionally, this work contributes to other studies by developing a receipt generator and creating a new dataset consisting of 1000 synthetic receipts and 711 real receipt images with corresponding annotations. This dataset is appropriate for document image processing and similar image-to-text studies (However, the dataset is not available in this repository). 

Different pre-trained models were fine-tuned on this dataset, resulting in significant enhancements. Moreover, an evaluation system with unified metrics was constructed to test various state-of-the-art OCR tools, such as EasyOCR, PP-OCR, and Tesseract, providing a comprehensive assessment of their performances in processing receipt images.
