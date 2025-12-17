import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { categoriesApi, Category } from '../../../api/categories';
import { useAuthStore } from '../../../store/authStore';

export default function CategoryList() {
    const queryClient = useQueryClient();
    const { user } = useAuthStore();

    const { data, isLoading } = useQuery({
        queryKey: ['categories-tree'],
        queryFn: categoriesApi.getTree,
    });

    const deleteMutation = useMutation({
        mutationFn: (id: number | string) => categoriesApi.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['categories-tree'] });
            queryClient.invalidateQueries({ queryKey: ['categories'] });
            alert('Xóa danh mục thành công');
        },
        onError: (err: any) => {
            alert('Lỗi: ' + (err.response?.data?.message || 'Không thể xóa danh mục'));
        }
    });

    const handleDelete = (id: number | string) => {
        if (window.confirm('Bạn có chắc chắn muốn xóa danh mục này?')) {
            deleteMutation.mutate(id);
        }
    };

    // Recursive component to render tree
    const CategoryItem = ({ category, level = 0 }: { category: Category; level?: number }) => (
        <>
            <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center" style={{ paddingLeft: `${level * 20}px` }}>
                        {level > 0 && <span className="text-gray-400 mr-2">↳</span>}
                        <div className="text-sm font-medium text-gray-900">{category.name}</div>
                    </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {category.slug}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {category.document_count || 0}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link to={`/admin/categories/edit/${category.id}`} className="text-indigo-600 hover:text-indigo-900 mr-4">
                        Sửa
                    </Link>
                    <button
                        onClick={() => handleDelete(category.id)}
                        className="text-red-600 hover:text-red-900"
                    >
                        Xóa
                    </button>
                </td>
            </tr>
            {category.children?.map(child => (
                <CategoryItem key={child.id} category={child} level={level + 1} />
            ))}
        </>
    );

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-900">Quản lý Danh mục</h1>
                <Link to="/admin/categories/create" className="btn btn-primary">
                    + Thêm danh mục
                </Link>
            </div>

            <div className="bg-white shadow rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Tên danh mục
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Slug
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Số văn bản
                            </th>
                            <th scope="col" className="relative px-6 py-3">
                                <span className="sr-only">Thao tác</span>
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {isLoading ? (
                            <tr>
                                <td colSpan={4} className="px-6 py-4 text-center">Đang tải...</td>
                            </tr>
                        ) : (
                            (data?.data?.data || []).map((cat: Category) => (
                                <CategoryItem key={cat.id} category={cat} />
                            ))
                        )}
                        {!isLoading && (data?.data?.data || []).length === 0 && (
                            <tr>
                                <td colSpan={4} className="px-6 py-4 text-center text-gray-500">Chưa có danh mục nào</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
