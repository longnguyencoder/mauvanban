import { useState } from 'react';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

interface GuideSection {
    id: number;
    title: string;
    content: string;
}

const defaultGuideSections: GuideSection[] = [
    {
        id: 1,
        title: '1. Thông tin biểu mẫu',
        content: 'Thông tin chi tiết về biểu mẫu, mục đích sử dụng và phạm vi áp dụng.'
    },
    {
        id: 2,
        title: '2. Đối tượng sử dụng',
        content: 'Các đối tượng được phép sử dụng biểu mẫu này theo quy định.'
    },
    {
        id: 3,
        title: '3. Trường hợp sử dụng',
        content: 'Các tình huống và trường hợp cụ thể cần sử dụng biểu mẫu.'
    },
    {
        id: 4,
        title: '4. Hướng dẫn điền mẫu',
        content: 'Hướng dẫn chi tiết từng bước để điền đầy đủ và chính xác thông tin vào biểu mẫu.'
    },
    {
        id: 5,
        title: '5. Quy trình nộp hồ sơ',
        content: 'Quy trình và thủ tục nộp hồ sơ sau khi hoàn thành biểu mẫu.'
    },
    {
        id: 6,
        title: '6. Phí và lệ phí (nếu có)',
        content: 'Thông tin về các khoản phí và lệ phí liên quan (nếu có).'
    },
    {
        id: 7,
        title: '7. Thời gian xử lý (nếu có)',
        content: 'Thời gian dự kiến để xử lý hồ sơ sau khi nộp.'
    },
    {
        id: 8,
        title: '8. Tài liệu, hồ sơ kèm theo',
        content: 'Danh sách các tài liệu và hồ sơ cần thiết kèm theo biểu mẫu.'
    },
    {
        id: 9,
        title: '9. Liên hệ hỗ trợ nhanh',
        content: 'Thông tin liên hệ để được hỗ trợ và giải đáp thắc mắc.'
    }
];

interface DocumentGuideSectionProps {
    sections?: GuideSection[];
}

export default function DocumentGuideSection({ sections = defaultGuideSections }: DocumentGuideSectionProps) {
    const [openSections, setOpenSections] = useState<number[]>([1]); // First section open by default

    const toggleSection = (id: number) => {
        setOpenSections(prev =>
            prev.includes(id)
                ? prev.filter(sectionId => sectionId !== id)
                : [...prev, id]
        );
    };

    return (
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl shadow-2xl overflow-hidden sticky top-8">
            <div className="p-6 border-b border-slate-700">
                <h2 className="text-xl font-bold text-white">Hướng dẫn Biểu mẫu</h2>
            </div>
            <div className="divide-y divide-slate-700">
                {sections.map((section) => {
                    const isOpen = openSections.includes(section.id);
                    return (
                        <div key={section.id} className="accordion-item">
                            <button
                                onClick={() => toggleSection(section.id)}
                                className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-slate-700/50 transition-colors duration-200"
                            >
                                <span className="text-slate-100 font-medium text-sm">
                                    {section.title}
                                </span>
                                <ChevronDownIcon
                                    className={`w-5 h-5 text-slate-400 transition-transform duration-300 ${isOpen ? 'transform rotate-180' : ''
                                        }`}
                                />
                            </button>
                            <div
                                className={`overflow-hidden transition-all duration-300 ${isOpen ? 'max-h-96' : 'max-h-0'
                                    }`}
                            >
                                <div className="px-6 pb-4 text-slate-300 text-sm leading-relaxed">
                                    {section.content}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
