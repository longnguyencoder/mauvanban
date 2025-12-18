import { CheckCircleIcon, DocumentTextIcon, BoltIcon } from '@heroicons/react/24/solid';

interface DocumentBadgesProps {
    verified?: boolean;
    guaranteed?: boolean;
    easyToUse?: boolean;
}

export default function DocumentBadges({
    verified = true,
    guaranteed = true,
    easyToUse = true
}: DocumentBadgesProps) {
    return (
        <div className="flex flex-wrap gap-3 mb-6">
            {verified && (
                <div className="badge badge-success">
                    <CheckCircleIcon className="w-4 h-4 mr-1.5" />
                    Luật sư đã kiểm duyệt
                </div>
            )}
            {guaranteed && (
                <div className="badge badge-info">
                    <DocumentTextIcon className="w-4 h-4 mr-1.5" />
                    Đảm bảo nội dung
                </div>
            )}
            {easyToUse && (
                <div className="badge badge-warning">
                    <BoltIcon className="w-4 h-4 mr-1.5" />
                    Dễ dàng sử dụng
                </div>
            )}
        </div>
    );
}
