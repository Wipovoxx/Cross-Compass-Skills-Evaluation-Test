import unittest
import tempfile
import os
from PIL import Image
import numpy as np
import glob
import shutil

class TestSpecialCharacterImageLoading(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.create_test_images_with_special_chars()
        
        self.image_names = []
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def create_test_images_with_special_chars(self):
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[:, :] = [255, 0, 0]  # Red image
        
        # Test files with various special characters
        test_filenames = [
            "Assassin’s Creed.jpg",           # Apostrophe
            "Assassin's Creed.png",           # Apostrophe with different extension
            "Café Müller.png",                # Accented characters
            "Test & Game.jpg",                # Ampersand
            "File (2023).png",                # Parentheses
            "Game-Title_v2.jpg",              # Hyphen and underscore
            "Spël Ñame.png",                  # More accented chars
            "测试图片.jpg",                    # Chinese characters
            "тест.png",                       # Cyrillic
            "🎮 Game.jpg",                    # Emoji
            "normal_file.jpg"                 # Normal filename for comparison
        ]
        
        self.expected_files = []
        for filename in test_filenames:
            try:
                filepath = os.path.join(self.test_dir, filename)
                Image.fromarray(test_image).save(filepath)
                
                if os.path.exists(filepath):
                    self.expected_files.append(filepath)
                    print(f"✓ Created: {filepath}")
                else:
                    print(f"✗ Failed to create: {filepath}")
            except Exception as e:
                print(f"✗ Error creating {filename}: {e}")
        
        print(f"Successfully created {len(self.expected_files)} test files")
    
    
    def loadImageNames(self, source_folder):
        
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif', "*.webp"]
        aux_image_names = []       
        if source_folder is not None and os.path.isdir(source_folder):
            # List all files in directory for debugging
            all_files = os.listdir(source_folder)
            print(f"\nAll files in directory: {all_files}")
            
            
            print("Loading images from:", source_folder)
            print("Total files in source folder:", len(all_files))
            
            for extension in extensions:                
                image_paths = glob.glob(os.path.join(source_folder, extension))                
                for image_path in image_paths:
                    print(f"Attempting to load: {image_path}")
                    try:
                        img = Image.open(image_path)
                        if img is not None:
                            aux_image_names.append(image_path)                           
                    except Exception as e:
                        print(f"Error loading image {image_path}: {e}")
            self.image_names = aux_image_names

    def test_load_images_with_special_characters(self):
        self.loadImageNames(self.test_dir)

        for imageName in self.image_names:
            self.assertIn(imageName, self.expected_files, f"Loaded image name '{imageName}' not found in expected files")