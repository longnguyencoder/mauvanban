import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import api, { API_BASE_URL } from '../../../api/axios';
import { categoriesApi, Category } from '../../../api/categories';

export default function CreateDocument() {
    const navigate = useNavigate();
    const [isUploading, setIsUploading] = useState(false);
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

    const [formData, setFormData] = useState({
        code: '',
        title: '',
        category_id: '',
        price: 0,
        description: '',
        content: '', // For preview text
        thumbnail_url: '',
        is_featured: false
    });

    const { data: categories } = useQuery({
        queryKey: ['categories'],
        queryFn: categoriesApi.getAll,
    });

    // 1. Thumbnail Upload Mutation
    const uploadThumbnailMutation = useMutation({
        mutationFn: async (file: File) => {
            const form = new FormData();
            form.append('file', file);
            const res = await api.post('/upload/image', form, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            return res.data;
        },
        onSuccess: (data) => {
            setIsUploading(false);
            setFormData(prev => ({
                ...prev,
                thumbnail_url: data.data.file_url
            }));
        },
        onError: () => setIsUploading(false)
    });

    // 2. Create Document Mutation (FormData)
    const createMutation = useMutation({
        mutationFn: async (data: any) => {
            const form = new FormData();

            // Append files
            selectedFiles.forEach(file => {
                form.append('files[]', file);
            });

            // Append other fields
            Object.keys(data).forEach(key => {
                form.append(key, data[key]);
            });

            return api.post('/admin/documents', form, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
        },
        onSuccess: () => {
            alert('Thêm văn bản thành công!');
            navigate('/admin/documents');
        },
        onError: (err: any) => {
            alert('Lỗi: ' + (err.response?.data?.message || 'Không thể tạo văn bản'));
        }
    });

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            const files = Array.from(e.target.files);
            setSelectedFiles(prev => [...prev, ...files]);

            // Auto-fill title from first file if empty
            if (!formData.title && files[0]) {
                const name = files[0].name.replace(/\.[^/.]+$/, "");
                setFormData(prev => ({ ...prev, title: name }));
            }
        }
    };

    const handleThumbnailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setIsUploading(true);
            uploadThumbnailMutation.mutate(e.target.files[0]);
        }
    };

    const removeFile = (index: number) => {
        setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        if (selectedFiles.length === 0) {
            if (!window.confirm('Bạn chưa chọn file tài liệu nào. Tiếp tục tạo văn bản rỗng?')) {
                return;
            }
        }

        createMutation.mutate(formData);
    };

    return (
        <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold mb-6">Thêm văn bản mới</h2>

            <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-8 grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Basic Info */}
                <div className="space-y-4 md:col-span-1">
                    <div>
                        <label className="label">Mã văn bản (Code) *</label>
                        <input
                            required
                            className="input"
                            placeholder="VD: HD-001"
                            value={formData.code}
                            onChange={e => setFormData({ ...formData, code: e.target.value })}
                        />
                    </div>

                    <div>
                        <label className="label">Tên văn bản *</label>
                        <input
                            required
                            className="input"
                            placeholder="Nhập tên văn bản"
                            value={formData.title}
                            onChange={e => setFormData({ ...formData, title: e.target.value })}
                        />
                    </div>

                    <div>
                        <label className="label">Danh mục *</label>
                        <select
                            required
                            className="input"
                            value={formData.category_id}
                            onChange={e => setFormData({ ...formData, category_id: e.target.value })}
                        >
                            <option value="">-- Chọn danh mục --</option>
                            {(categories?.data?.data || []).map((cat: Category) => (
                                <option key={cat.id} value={cat.id}>{cat.name}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="label">Giá (VNĐ)</label>
                        <input
                            type="number"
                            className="input"
                            min="0"
                            value={formData.price}
                            onChange={e => setFormData({ ...formData, price: Number(e.target.value) })}
                        />
                        <p className="text-xs text-gray-500 mt-1">Để 0 nếu miễn phí</p>
                    </div>

                    <div className="flex items-center gap-2 mt-4">
                        <input
                            type="checkbox"
                            id="featured"
                            checked={formData.is_featured}
                            onChange={e => setFormData({ ...formData, is_featured: e.target.checked })}
                        />
                        <label htmlFor="featured">Đánh dấu là văn bản nổi bật</label>
                    </div>
                </div>

                {/* Upload & Details */}
                <div className="space-y-4 md:col-span-1">
                    {/* Main Document Upload */}
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 hover:bg-gray-50 transition">
                        <label className="cursor-pointer block text-center mb-4">
                            <span className="text-3xl block mb-2">📄</span>
                            <span className="font-bold text-gray-700 block">Chọn File Tài Liệu</span>
                            <span className="text-sm text-gray-500">
                                Click để chọn nhiều file (.doc, .pdf)
                            </span>
                            <input
                                type="file"
                                className="hidden"
                                multiple
                                accept=".pdf,.doc,.docx,.xls,.xlsx"
                                onChange={handleFileChange}
                            />
                        </label>

                        {/* File List */}
                        {selectedFiles.length > 0 && (
                            <div className="space-y-2 max-h-40 overflow-y-auto">
                                {selectedFiles.map((file, index) => (
                                    <div key={index} className="flex items-center justify-between bg-gray-100 p-2 rounded text-sm">
                                        <span className="truncate max-w-[200px]">{file.name}</span>
                                        <button
                                            type="button"
                                            onClick={() => removeFile(index)}
                                            className="text-red-500 hover:text-red-700"
                                        >
                                            ✕
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Thumbnail Upload */}
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:bg-gray-50 transition">
                        <label className="cursor-pointer block">
                            <span className="text-3xl block mb-2">🖼️</span>
                            <span className="font-bold text-gray-700 block">Ảnh Bìa (Thumbnail)</span>
                            <span className="text-sm text-gray-500">
                                {isUploading ? 'Đang upload...' : formData.thumbnail_url ? 'Đã upload thumbnail' : 'Click để chọn ảnh (.png, .jpg)'}
                            </span>
                            <input
                                type="file"
                                className="hidden"
                                accept="image/*"
                                onChange={handleThumbnailChange}
                                disabled={isUploading}
                            />
                        </label>
                        {formData.thumbnail_url && (
                            <div className="mt-2 text-center">
                                <img
                                    src={`${API_BASE_URL}${formData.thumbnail_url}`}
                                    alt="Preview"
                                    className="h-20 mx-auto object-cover rounded border"
                                />
                            </div>
                        )}
                    </div>

                    <div>
                        <label className="label">Mô tả ngắn</label>
                        <textarea
                            className="input h-24"
                            placeholder="Mô tả về văn bản này..."
                            value={formData.description}
                            onChange={e => setFormData({ ...formData, description: e.target.value })}
                        ></textarea>
                    </div>
                </div>

                {/* Action */}
                <div className="md:col-span-2 pt-4 border-t flex justify-end gap-3">
                    <button type="button" onClick={() => navigate('/admin/documents')} className="btn btn-secondary">
                        Hủy bỏ
                    </button>
                    <button
                        type="submit"
                        className="btn btn-primary px-8"
                        disabled={createMutation.isPending || isUploading}
                    >
                        {createMutation.isPending ? 'Đang lưu...' : 'Tạo văn bản'}
                    </button>
                </div>

            </form>
        </div>
    );
}
