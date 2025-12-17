import { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { categoriesApi, Category } from '../../../api/categories';
import api from '../../../api/axios';

// Extend Category type to include display_order if missing
interface CategoryWithOrder extends Category {
    display_order?: number;
}


export default function CreateCategory() {
    const { id } = useParams(); // If ID exists, it's Edit mode
    const isEdit = !!id;
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const [formData, setFormData] = useState({
        name: '',
        description: '',
        parent_id: '',
        icon: '',
        display_order: 0
    });

    const [uploading, setUploading] = useState(false);

    // Fetch existing data if edit
    const { data: categoryData } = useQuery({
        queryKey: ['category', id],
        queryFn: () => categoriesApi.getById(id!),
        enabled: isEdit
    });

    // Fetch all categories for parent selection
    const { data: categoriesTree } = useQuery({
        queryKey: ['categories-tree'],
        queryFn: categoriesApi.getTree,
    });

    useEffect(() => {
        if (categoryData?.data?.data) {
            const cat = categoryData.data.data;
            setFormData({
                name: cat.name,
                description: cat.description || '',
                parent_id: cat.parent_id?.toString() || '',
                icon: cat.icon || '',
                display_order: (cat as any).display_order || 0
            });
        }
    }, [categoryData]);

    const mutation = useMutation({
        mutationFn: (data: any) => {
            const payload: any = {
                ...data,
                display_order: Number(data.display_order)
            };

            if (data.parent_id) {
                payload.parent_id = data.parent_id;
            }

            if (isEdit) {
                return categoriesApi.update(id!, payload);
            } else {
                return categoriesApi.create(payload);
            }
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['categories-tree'] });
            queryClient.invalidateQueries({ queryKey: ['categories'] });
            alert(isEdit ? 'Cập nhật danh mục thành công' : 'Thêm danh mục thành công');
            navigate('/admin/categories');
        },
        onError: (err: any) => {
            alert('Lỗi: ' + (err.response?.data?.message || 'Có lỗi xảy ra'));
        }
    });

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const formDataUpload = new FormData();
            formDataUpload.append('file', file);

            setUploading(true);
            try {
                // Use the API instance to handle auth headers automatically if configured, 
                // but for form-data, sometimes better to use axios directly or ensure api instance handles content-type.
                // Our api instance (axios.ts) handles headers.
                // Endpoint: /admin/upload/image is NOT correct based on upload_controller. It's /upload/image
                // Check controller: upload_ns = Namespace('upload'...) -> /upload
                // Resource UploadImage route: /image -> /upload/image
                // So full path: /api/upload/image (assuming default prefix)

                const res = await api.post('/upload/image', formDataUpload, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                });

                if (res.data.success) {
                    setFormData(prev => ({
                        ...prev,
                        icon: res.data.data.file_url
                    }));
                }
            } catch (err: any) {
                alert('Lỗi upload ảnh: ' + (err.response?.data?.message || err.message));
            } finally {
                setUploading(false);
            }
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        mutation.mutate(formData);
    };

    // Flatten tree for select options
    const renderOptions = (cats: Category[], level = 0): JSX.Element[] => {
        let options: JSX.Element[] = [];
        cats.forEach(cat => {
            // Prevent selecting itself as parent
            if (isEdit && cat.id.toString() === id) return;

            options.push(
                <option key={cat.id} value={cat.id}>
                    {'-'.repeat(level)} {cat.name}
                </option>
            );
            if (cat.children) {
                options = [...options, ...renderOptions(cat.children, level + 1)];
            }
        });
        return options;
    };

    return (
        <div className="max-w-2xl mx-auto">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">
                {isEdit ? 'Cập nhật danh mục' : 'Thêm danh mục mới'}
            </h1>

            <div className="bg-white shadow rounded-lg p-6">
                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Name */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Tên danh mục <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            required
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            className="input"
                            placeholder="Ví dụ: Hợp đồng"
                        />
                    </div>

                    {/* Parent */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Danh mục cha
                        </label>
                        <select
                            value={formData.parent_id}
                            onChange={(e) => setFormData({ ...formData, parent_id: e.target.value })}
                            className="input"
                        >
                            <option value="">-- Không có (Danh mục gốc) --</option>
                            {renderOptions(categoriesTree?.data?.data || [])}
                        </select>
                    </div>

                    {/* Icon / Image */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Icon hoặc Ảnh đại diện
                        </label>
                        <div className="space-y-3">
                            {/* Option 1: Text input for Icon Class or URL */}
                            <input
                                type="text"
                                value={formData.icon}
                                onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                                className="input"
                                placeholder="Nhập tên icon (VD: briefcase) hoặc URL ảnh"
                            />

                            {/* Option 2: Upload Image */}
                            <div className="flex items-center gap-4">
                                <label className="block text-sm text-gray-500">Hoặc tải ảnh lên:</label>
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileChange}
                                    disabled={uploading}
                                    className="text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                                />
                                {uploading && <span className="text-sm text-blue-500">Đang tải lên...</span>}
                            </div>

                            {/* Preview */}
                            {formData.icon && (
                                <div className="mt-2">
                                    <p className="text-xs text-gray-500 mb-1">Xem trước:</p>
                                    {formData.icon.startsWith('/') || formData.icon.startsWith('http') ? (
                                        <img
                                            src={formData.icon.startsWith('/') ? `http://localhost:5000${formData.icon}` : formData.icon}
                                            alt="Category Icon"
                                            className="w-16 h-16 object-contain border rounded-lg p-1"
                                        />
                                    ) : (
                                        <div className="w-16 h-16 border rounded-lg flex items-center justify-center bg-gray-50 text-gray-400">
                                            (Icon text)
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Description */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Mô tả
                        </label>
                        <textarea
                            rows={3}
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            className="input"
                        />
                    </div>

                    {/* Actions */}
                    <div className="flex justify-end gap-3 pt-4">
                        <button
                            type="button"
                            onClick={() => navigate('/admin/categories')}
                            className="btn btn-secondary"
                        >
                            Hủy
                        </button>
                        <button
                            type="submit"
                            disabled={mutation.isPending || uploading}
                            className="btn btn-primary"
                        >
                            {mutation.isPending ? 'Đang lưu...' : (isEdit ? 'Cập nhật' : 'Thêm mới')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
