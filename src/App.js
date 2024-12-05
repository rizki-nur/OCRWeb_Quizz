import React, { useState } from 'react';
import { Card, Button, ProgressBar } from 'react-bootstrap';

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [ocrResult, setOcrResult] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file); // Simpan file untuk diunggah
    }
  };

  const handleOCRProcess = async () => {
    if (!selectedImage) {
      alert('Pilih gambar terlebih dahulu!');
      return;
    }
  
    setIsProcessing(true);
  
    const formData = new FormData();
    formData.append('image', selectedImage);
  
    try {
      const response = await fetch('http://127.0.0.1:5000/process-ocr', {
        method: 'POST',
        body: formData,
      });
  
      const data = await response.json();
  
      // Debugging respons dari Flask
      console.log("Respons dari server Flask:", data);
  
      if (response.ok && !data.error) {
        setOcrResult(
          `Judul: ${data.title || "N/A"}\nPenulis: ${data.author || "N/A"}\nDeskripsi: ${data.description || "N/A"}`
        );
      } else {
        setOcrResult(`Error: ${data.error || "Terjadi kesalahan."}`);
      }
    } catch (error) {
      console.error("Terjadi kesalahan:", error);
      setOcrResult('Terjadi kesalahan saat memproses OCR.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="container my-4">
      <h1 className="text-center mb-4">OCR Pencari Buku</h1>
      <div className="d-flex flex-column align-items-center">
        <input
          type="file"
          accept="image/*"
          className="form-control mb-3"
          onChange={handleImageUpload}
        />
        {selectedImage && (
          <Card style={{ width: '80%', maxWidth: '600px' }} className="mb-3">
            <Card.Img
              variant="top"
              src={URL.createObjectURL(selectedImage)}
              alt="Uploaded preview"
              style={{ objectFit: 'cover', height: '300px' }}
            />
            <Card.Body>
              <Card.Title className="text-center">Hasil OCR</Card.Title>
              <Card.Text className="text-muted" style={{ height: '100px', overflowY: 'auto' }}>
                {ocrResult || "Hasil akan muncul di sini setelah proses OCR."}
              </Card.Text>
              <div className="d-flex justify-content-center">
                <Button
                  variant="primary"
                  onClick={handleOCRProcess}
                  disabled={isProcessing}
                >
                  {isProcessing ? 'Memproses...' : 'Proses OCR'}
                </Button>
              </div>
              {isProcessing && <ProgressBar animated now={100} className="mt-3" />}
            </Card.Body>
          </Card>
        )}
      </div>
    </div>
  );
}

export default App;
