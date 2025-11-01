import React, { useState, useEffect, useCallback } from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import api from '../../services/api';

interface DocumentEditorViewProps {
  channelId: string;
}

const DocumentEditorView: React.FC<DocumentEditorViewProps> = ({ channelId }) => {
  const [content, setContent] = useState<string>('');
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [saveTimeout, setSaveTimeout] = useState<NodeJS.Timeout | null>(null);

  // Fetch document content on mount or when channelId changes
  useEffect(() => {
    const fetchDocument = async () => {
      try {
        const response = await api.get(`/documents/${channelId}`);
        setContent(response.data.content || '');
      } catch (error) {
        console.error('Error fetching document:', error);
        // Initialize with empty content if document doesn't exist
        setContent('');
      }
    };

    fetchDocument();
  }, [channelId]);

  // Auto-save with debounce
  const saveDocument = useCallback(async (contentToSave: string) => {
    try {
      setIsSaving(true);
      await api.put(`/documents/${channelId}`, { content: contentToSave });
      setLastSaved(new Date());
    } catch (error) {
      console.error('Error saving document:', error);
    } finally {
      setIsSaving(false);
    }
  }, [channelId]);

  // Handle content change with debounced auto-save
  const handleChange = (value: string) => {
    setContent(value);

    // Clear existing timeout
    if (saveTimeout) {
      clearTimeout(saveTimeout);
    }

    // Set new timeout for auto-save (2 seconds after user stops typing)
    const timeout = setTimeout(() => {
      saveDocument(value);
    }, 2000);

    setSaveTimeout(timeout);
  };

  // Manual save handler
  const handleManualSave = () => {
    if (saveTimeout) {
      clearTimeout(saveTimeout);
    }
    saveDocument(content);
  };

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (saveTimeout) {
        clearTimeout(saveTimeout);
      }
    };
  }, [saveTimeout]);

  // Quill modules configuration
  const modules = {
    toolbar: [
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'list': 'ordered' }, { 'list': 'bullet' }],
      [{ 'indent': '-1' }, { 'indent': '+1' }],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'align': [] }],
      ['link', 'image', 'code-block'],
      ['clean']
    ]
  };

  const formats = [
    'header',
    'bold', 'italic', 'underline', 'strike',
    'list', 'bullet',
    'indent',
    'color', 'background',
    'align',
    'link', 'image', 'code-block'
  ];

  return (
    <div className="flex flex-col h-full bg-dark-bg">
      {/* Header with save status */}
      <div className="flex items-center justify-between px-6 py-3 bg-dark-surface border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white">Document Editor</h2>
        <div className="flex items-center gap-4">
          {lastSaved && (
            <span className="text-sm text-gray-400">
              Last saved: {lastSaved.toLocaleTimeString()}
            </span>
          )}
          {isSaving && (
            <span className="text-sm text-accent-primary">Saving...</span>
          )}
          <button
            onClick={handleManualSave}
            disabled={isSaving}
            className="px-4 py-2 bg-accent-primary text-white rounded-lg hover:bg-accent-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Save
          </button>
        </div>
      </div>

      {/* Editor container */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg">
          <ReactQuill
            theme="snow"
            value={content}
            onChange={handleChange}
            modules={modules}
            formats={formats}
            className="h-full"
            style={{ minHeight: '500px' }}
          />
        </div>
      </div>
    </div>
  );
};

export default DocumentEditorView;
