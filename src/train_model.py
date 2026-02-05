"""
Model training and ONNX export script for वाणीCheck
Trains binary classification head on Wav2Vec 2.0 for deepfake detection
"""

import os
import torch
import numpy as np
from transformers import (
    AutoProcessor,
    AutoModelForAudioClassification,
    TrainingArguments,
    Trainer,
)
from datasets import Dataset, DatasetDict
import librosa
from pathlib import Path

# Configuration
MODEL_NAME = "facebook/wav2vec2-xlsr-53-english"
OUTPUT_DIR = "./models/vanicheck-deepfake-detector"
SAMPLE_RATE = 16000
MAX_AUDIO_LENGTH = 10  # seconds

class DeepfakeDataset:
    """Utility to create training dataset"""
    
    @staticmethod
    def create_dummy_dataset(num_samples=100):
        """
        Create a dummy dataset for demonstration
        In production, use real human vs AI-generated samples
        """
        audio_data = []
        labels = []
        
        # Generate synthetic human-like audio (0 = HUMAN)
        for _ in range(num_samples // 2):
            # Simulate human speech with natural F0 variations
            duration = np.random.uniform(2, 8)
            t = np.arange(int(SAMPLE_RATE * duration)) / SAMPLE_RATE
            f0 = 100 + 50 * np.sin(2 * np.pi * 0.5 * t)  # Varying F0
            audio = np.sin(2 * np.pi * f0 * t) * 0.5
            audio += np.random.normal(0, 0.01, len(audio))  # Add natural noise
            
            audio_data.append(audio)
            labels.append(0)
        
        # Generate synthetic TTS-like audio (1 = AI_GENERATED)
        for _ in range(num_samples // 2):
            # Simulate TTS with consistent F0
            duration = np.random.uniform(2, 8)
            t = np.arange(int(SAMPLE_RATE * duration)) / SAMPLE_RATE
            f0 = np.full_like(t, 120)  # Constant F0
            audio = np.sin(2 * np.pi * f0 * t) * 0.5
            # Less natural variations
            audio += np.random.normal(0, 0.005, len(audio))
            
            audio_data.append(audio)
            labels.append(1)
        
        # Convert to dataset format
        dataset_dict = {
            "audio": [{"array": np.pad(a, (0, max(0, int(SAMPLE_RATE * MAX_AUDIO_LENGTH) - len(a))), mode='constant'), 
                       "sampling_rate": SAMPLE_RATE} for a in audio_data],
            "label": labels
        }
        
        return Dataset.from_dict(dataset_dict)

def prepare_dataset(dataset):
    """Prepare dataset for training"""
    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    
    def process_function(examples):
        audio_list = [x["array"] for x in examples["audio"]]
        
        # Process audio
        processed = processor(
            audio_list,
            sampling_rate=SAMPLE_RATE,
            max_length=int(SAMPLE_RATE * MAX_AUDIO_LENGTH),
            truncation=True,
            padding=True,
            return_tensors="pt"
        )
        
        return {
            "input_values": processed["input_values"],
            "labels": torch.tensor(examples["label"])
        }
    
    return dataset.map(
        process_function,
        batched=True,
        remove_columns=["audio"]
    )

def train_deepfake_detector(dataset=None, epochs=5):
    """Train the deepfake detection model"""
    
    # Create dataset if not provided
    if dataset is None:
        print("Creating dummy dataset for demonstration...")
        dataset = DeepfakeDataset.create_dummy_dataset(num_samples=200)
    
    # Split dataset
    dataset = dataset.train_test_split(test_size=0.2)
    
    # Prepare dataset
    print("Processing dataset...")
    train_dataset = prepare_dataset(dataset["train"])
    eval_dataset = prepare_dataset(dataset["test"])
    
    # Load model
    print(f"Loading model {MODEL_NAME}...")
    model = AutoModelForAudioClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2,
        ignore_mismatched_sizes=True
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=epochs,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )
    
    # Train
    print("Starting training...")
    trainer.train()
    
    # Save model
    print(f"Saving model to {OUTPUT_DIR}...")
    model.save_pretrained(OUTPUT_DIR)
    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    processor.save_pretrained(OUTPUT_DIR)
    
    print("Training complete!")
    return model, processor

def export_to_onnx(model_path=OUTPUT_DIR):
    """Export model to ONNX format for optimized inference"""
    try:
        import torch.onnx
        from torch import onnx
        
        print(f"Loading model from {model_path}...")
        model = AutoModelForAudioClassification.from_pretrained(model_path)
        processor = AutoProcessor.from_pretrained(model_path)
        
        # Create dummy input
        dummy_audio = torch.randn(1, SAMPLE_RATE * 8)
        dummy_input = processor(dummy_audio, sampling_rate=SAMPLE_RATE, return_tensors="pt")
        
        # Export to ONNX
        onnx_path = os.path.join(model_path, "model.onnx")
        print(f"Exporting to {onnx_path}...")
        
        onnx.export(
            model,
            tuple(dummy_input.values()),
            onnx_path,
            input_names=list(dummy_input.keys()),
            output_names=["logits"],
            opset_version=14,
            dynamic_axes={
                'input_values': {0: 'batch_size', 1: 'sequence_length'},
                'attention_mask': {0: 'batch_size', 1: 'sequence_length'},
                'logits': {0: 'batch_size'}
            }
        )
        
        print(f"ONNX model exported successfully to {onnx_path}")
        
    except Exception as e:
        print(f"ONNX export failed (this is optional): {e}")
        print("Continuing without ONNX export...")

if __name__ == "__main__":
    print("=" * 60)
    print("वाणीCheck - Deepfake Detection Model Training")
    print("=" * 60)
    
    # Create output directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # Train model
    model, processor = train_deepfake_detector(epochs=3)
    
    # Export to ONNX (optional, for production deployment)
    export_to_onnx()
    
    print("\nModel training complete!")
    print(f"Model saved to: {OUTPUT_DIR}")
