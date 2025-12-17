import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { categoriesApi } from '../api/categories';
import {
    BriefcaseIcon,
    AcademicCapIcon,
    ScaleIcon,
    BuildingOfficeIcon,
    HomeIcon,
    CurrencyDollarIcon,
    HeartIcon,
    DocumentTextIcon,
    ClipboardDocumentCheckIcon,
    FolderIcon
} from '@heroicons/react/24/outline';

const SERVER_URL = 'http://localhost:5000'; // Should be from config/env

export default function Categories() {
    const { data: categories, isLoading } = useQuery({
        queryKey: ['categories'],
        queryFn: categoriesApi.getAll,
    });

    if (isLoading) return <div className="text-center py-20">Đang tải...</div>;

    const list = categories?.data?.data || [];

    // Map DB icon strings to HeroIcons
    const getIcon = (iconName: string) => {
        const className = "w-12 h-12 mx-auto mb-4 text-primary-600 group-hover:scale-110 transition-transform duration-300 object-contain"; // Added object-contain for images

        // Method 1: Check for Image URL
        if (iconName && (iconName.startsWith('/') || iconName.startsWith('http'))) {
            const imageUrl = iconName.startsWith('/') ? `${SERVER_URL}${iconName}` : iconName;
            return <img src={imageUrl} alt="icon" className={className} />;
        }

        // Method 2: HeroIcons mapping
        switch (iconName) {
            case 'briefcase': return <BriefcaseIcon className={className} />;
            case 'graduation-cap': return <AcademicCapIcon className={className} />;
            case 'gavel': return <ScaleIcon className={className} />;
            case 'building': return <BuildingOfficeIcon className={className} />;
            case 'home': return <HomeIcon className={className} />;
            case 'dollar-sign': return <CurrencyDollarIcon className={className} />;
            case 'heartbeat': return <HeartIcon className={className} />;
            case 'file-text': return <DocumentTextIcon className={className} />;
            case 'file-contract': return <ClipboardDocumentCheckIcon className={className} />;
            default:
                // Check if it's an emoji or other text, render if short
                if (iconName && !iconName.match(/^[a-z0-9-]+$/) && iconName.length < 5) {
                    return <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">{iconName}</div>;
                }
                return <FolderIcon className={className} />;
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center text-primary-800">Danh mục văn bản</h1>

            {list.length === 0 ? (
                <div className="text-center text-gray-500">Chưa có danh mục nào.</div>
            ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                    {list.map((cat: any) => (
                        <Link
                            key={cat.id}
                            to={`/documents?category=${cat.id}`}
                            className="bg-white rounded-xl shadow-sm hover:shadow-lg p-8 text-center transition-all border border-gray-100 hover:border-primary-200 group flex flex-col items-center"
                        >
                            {getIcon(cat.icon)}

                            <h3 className="font-bold text-gray-900 group-hover:text-primary-700 transition-colors text-lg">
                                {cat.name}
                            </h3>
                            <p className="text-sm text-gray-500 mt-2">
                                {cat.documents_count || 0} văn bản
                            </p>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}
