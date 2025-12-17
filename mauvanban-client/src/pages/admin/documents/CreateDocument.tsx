import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import api from '../../../api/axios';
import { categoriesApi, Category } from '../../../api/categories';

export default function CreateDocument() {
    const navigate = useNavigate();
    const [isUploading, setIsUploading] = useState(false);
    const [formData, setFormData] = useState({
        code: '',
        title: '',
        category_id: '',
        price: 0,
        description: '',
        content: '', // For preview text
        file_url: '',
        file_type: '',
        thumbnail_url: '',
        is_featured: false
    });

    const { data: categories } = useQuery({
        queryKey: ['categories'],
        queryFn: categoriesApi.getAll,
    });

    // 1. Upload Mutation
    const uploadMutation = useMutation({
        mutationFn: async ({ file, isThumbnail }: { file: File; isThumbnail: boolean }) => {
            const form = new FormData();
            form.append('file', file);
            // Select endpoint based on type
            const endpoint = isThumbnail ? '/upload/image' : '/upload/document';

            const res = await api.post(endpoint, form, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            return { ...res.data, isThumbnail };
        },
        onSuccess: (data) => {
            setIsUploading(false);
            if (data.isThumbnail) {
                // Update thumbnail
                setFormData(prev => ({
                    ...prev,
                    thumbnail_url: data.data.file_url
                }));
            } else {
                // Update main document
                setFormData(prev => ({
                    ...prev,
                    file_url: data.data.file_url,
                    file_type: data.data.file_type
                }));
                // Auto-fill title if empty and not thumbnail
                if (!formData.title && data.data.original_filename) {
                    setFormData(prev => ({ ...prev, title: data.data.original_filename }));
                }
            }
        },
        onError: () => setIsUploading(false)
    });

    // 2. Create Document Mutation
    const createMutation = useMutation({
        mutationFn: (data: any) => api.post('/admin/documents/json', data),
        onSuccess: () => {
            alert('Thêm văn bản thành công!');
            navigate('/admin/documents');
        },
        onError: (err: any) => {
            alert('Lỗi: ' + (err.response?.data?.message || 'Không thể tạo văn bản'));
        }
    });

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, isThumbnail: boolean = false) => {
        if (e.target.files && e.target.files[0]) {
            setIsUploading(true);
            uploadMutation.mutate({ file: e.target.files[0], isThumbnail });
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.file_url) {
            alert('Vui lòng upload file văn bản chính!');
            return;
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
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:bg-gray-50 transition">
                        <label className="cursor-pointer block">
                            <span className="text-3xl block mb-2">📄</span>
                            <span className="font-bold text-gray-700 block">File Văn Bản Chính *</span>
                            <span className="text-sm text-gray-500">
                                {isUploading ? 'Đang upload...' : formData.file_url ? 'Đã upload: ' + formData.file_url.split('/').pop() : 'Click để chọn file (.doc, .pdf)'}
                            </span>
                            <input
                                type="file"
                                className="hidden"
                                accept=".pdf,.doc,.docx,.xls,.xlsx"
                                onChange={(e) => handleFileChange(e, false)}
                                disabled={isUploading}
                            />
                        </label>
                    </div>

                    {/* Thumbnail Upload */}
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:bg-gray-50 transition">
                        <label className="cursor-pointer block">
                            <span className="text-3xl block mb-2">🖼️</span>
                            <span className="font-bold text-gray-700 block">Ảnh Bìa (Thumbnail)</span>
                            <span className="text-sm text-gray-500">
                                {isUploading ? 'Đang upload...' : formData.thumbnail_url ? 'Đã upload: ' + formData.thumbnail_url.split('/').pop() : 'Click để chọn ảnh (.png, .jpg, .pdf)'}
                            </span>
                            <input
                                type="file"
                                className="hidden"
                                accept="image/*,.pdf"
                                onChange={(e) => handleFileChange(e, true)}
                                disabled={isUploading}
                            />
                        </label>
                        {formData.thumbnail_url && (
                            <div className="mt-2 text-center">
                                {formData.thumbnail_url.toLowerCase().endsWith('.pdf') ? (
                                    <div className="text-red-500 font-bold border p-2 rounded">PDF Thumbnail</div>
                                ) : (
                                    <img
                                        src={`http://localhost:5000${formData.thumbnail_url}`}
                                        alt="Preview"
                                        className="h-20 mx-auto object-cover rounded border"
                                    />
                                )}
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
