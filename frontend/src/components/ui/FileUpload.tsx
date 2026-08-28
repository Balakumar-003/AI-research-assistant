import React, { useState } from 'react';
import { UploadCloud, X, FileText } from 'lucide-react';
import { Button } from '../common/Button';
import './FileUpload.css';

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>;
  maxSizeMB?: number;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUpload, maxSizeMB = 10 }) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateFile = (selectedFile: File) => {
    if (selectedFile.type !== 'application/pdf') {
      setError('Only PDF files are allowed');
      return false;
    }
    if (selectedFile.size > maxSizeMB * 1024 * 1024) {
      setError(`File size must be less than ${maxSizeMB}MB`);
      return false;
    }
    setError('');
    return true;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
      }
    }
  };

  const handleUploadSubmit = async () => {
    if (!file) return;
    setIsUploading(true);
    try {
      await onUpload(file);
      setFile(null); // Reset on success
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="file-upload-container">
      {!file ? (
        <div 
          className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <UploadCloud size={48} className="upload-icon" />
          <h3>Drag and drop your PDF here</h3>
          <p>or click to browse files</p>
          <input 
            type="file" 
            accept="application/pdf"
            onChange={handleChange}
            className="file-input"
          />
        </div>
      ) : (
        <div className="file-preview">
          <div className="file-info">
            <FileText size={24} className="text-primary" />
            <span className="file-name">{file.name}</span>
            <span className="file-size">({(file.size / (1024 * 1024)).toFixed(2)} MB)</span>
          </div>
          <button className="remove-file-btn" onClick={() => setFile(null)} disabled={isUploading}>
            <X size={20} />
          </button>
        </div>
      )}

      {error && <div className="upload-error">{error}</div>}

      {file && (
        <Button 
          className="upload-submit-btn w-full mt-4" 
          onClick={handleUploadSubmit}
          isLoading={isUploading}
        >
          Upload Document
        </Button>
      )}
    </div>
  );
};


