import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsApi } from '../../../api/documents';
import { categoriesApi } from '../../../api/categories';
import api, { API_BASE_URL } from '../../../api/axios';

export default function EditDocument() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    // Form State
    const [formData, setFormData] = useState({
        code: '',
        title: '',
        price: 0,
        category_id: '',
        is_featured: false,
        description: '',
        content: '',
        thumbnail_url: ''
    });

    const [uploading, setUploading] = useState(false);

    // Fetch Document
    const { data: documentData, isLoading: isLoadingDoc } = useQuery({
        queryKey: ['document', id],
        queryFn: () => documentsApi.getById(id!),
        enabled: !!id,
    });

    // Fetch Categories for dropdown
    const { data: categoriesData } = useQuery({
        queryKey: ['categories'],
        queryFn: () => categoriesApi.getAll(),
    });

    useEffect(() => {
        if (documentData?.data?.data) {
            const doc = documentData.data.data;
            setFormData({
                code: doc.code || '',
                title: doc.title || '',
                price: doc.price || 0,
                category_id: doc.category?.id ? String(doc.category.id) : (doc.category_id ? String(doc.category_id) : ''),
                is_featured: doc.is_featured || false,
                description: doc.description || '',
                content: doc.content || '',
                thumbnail_url: doc.thumbnail_url || ''
            });
        }
    }, [documentData]);

    const updateMutation = useMutation({
        mutationFn: (data: any) => documentsApi.update(id!, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-documents'] });
            queryClient.invalidateQueries({ queryKey: ['document', id] });
            alert('Cập nhật văn bản thành công!');
            navigate('/admin/documents');
        },
        onError: (error: any) => {
            alert('Lỗi: ' + (error?.response?.data?.message || 'Có lỗi xảy ra'));
        }
    });

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const formDataUpload = new FormData();
            formDataUpload.append('file', file);

            setUploading(true);
            try {
                // Upload to /api/upload/image using configured api instance
                const res = await api.post('/upload/image', formDataUpload, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                });

                if (res.data.success) {
                    setFormData(prev => ({
                        ...prev,
                        thumbnail_url: res.data.data.file_url
                    }));
                }
            } catch (err: any) {
                alert('Lỗi upload ảnh: ' + (err.response?.data?.message || err.message));
            } finally {
                setUploading(false);
            }
        }
    };



    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value, type } = e.target;
        const val = type === 'checkbox' ? (e.target as HTMLInputElement).checked : value;

        setFormData(prev => ({
            ...prev,
            [name]: type === 'number' ? Number(val) : val
        }));
    };

    const onSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        updateMutation.mutate(formData);
    };

    if (isLoadingDoc) return <div>Đang tải...</div>;
    const categories = categoriesData?.data?.data || [];

    return (
        <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-2xl font-bold mb-6">Chỉnh sửa văn bản</h2>

            <form onSubmit={onSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Mã văn bản</label>
                        <input
                            name="code"
                            value={formData.code}
                            // Code is READ ONLY
                            readOnly
                            disabled
                            type="text"
                            className="w-full border-gray-300 rounded-md shadow-sm bg-gray-100 cursor-not-allowed p-2 border"
                        />
                        <p className="text-xs text-gray-500 mt-1">Mã văn bản không thể thay đổi.</p>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Tiêu đề</label>
                        <input
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            type="text"
                            className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 p-2 border"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Danh mục</label>
                        <select
                            name="category_id"
                            value={formData.category_id}
                            onChange={handleChange}
                            className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 p-2 border"
                        >
                            <option value="">-- Chọn danh mục --</option>
                            {categories.map((cat: any) => (
                                <option key={cat.id} value={cat.id}>{cat.name}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Giá (VNĐ)</label>
                        <input
                            name="price"
                            value={formData.price}
                            onChange={handleChange}
                            type="number"
                            className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 p-2 border"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Thumbnail/Ảnh bìa</label>
                        <div className="space-y-3">
                            <div className="flex gap-2">
                                <input
                                    name="thumbnail_url"
                                    value={formData.thumbnail_url}
                                    onChange={handleChange}
                                    type="text"
                                    className="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 p-2 border"
                                    placeholder="Nhập URL hoặc upload ảnh bên dưới..."
                                />
                            </div>

                            <div className="flex items-center gap-4">
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileChange}
                                    disabled={uploading}
                                    className="text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                                />
                                {uploading && <span className="text-sm text-blue-500">Đang tải lên...</span>}
                            </div>

                            {formData.thumbnail_url && (
                                <div className="mt-2">
                                    <p className="text-xs text-gray-500 mb-1">Xem trước:</p>
                                    <img
                                        src={formData.thumbnail_url.startsWith('/') ? `${API_BASE_URL}${formData.thumbnail_url}` : formData.thumbnail_url}
                                        alt="Preview"
                                        className="h-32 w-auto object-cover rounded border shadow-sm"
                                    />
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="flex items-center mt-6">
                        <input
                            name="is_featured"
                            checked={formData.is_featured}
                            onChange={handleChange}
                            type="checkbox"
                            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                        />
                        <label className="ml-2 block text-sm text-gray-900">
                            Văn bản nổi bật
                        </label>
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Mô tả ngắn</label>
                    <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        rows={3}
                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 p-2 border"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nội dung (Preview)</label>
                    <textarea
                        name="content"
                        value={formData.content}
                        onChange={handleChange}
                        rows={10}
                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 font-mono text-sm p-2 border"
                        placeholder="Nội dung văn bản..."
                    />
                </div>

                <div className="flex justify-end gap-4 pt-4 border-t">
                    <button
                        type="button"
                        onClick={() => navigate('/admin/documents')}
                        className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                        Hủy
                    </button>
                    <button
                        type="submit"
                        disabled={updateMutation.isPending}
                        className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                    >
                        {updateMutation.isPending ? 'Đang lưu...' : 'Lưu thay đổi'}
                    </button>
                </div>
            </form>
        </div>
    );
}
