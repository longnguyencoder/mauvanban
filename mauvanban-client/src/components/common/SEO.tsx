import { useEffect } from 'react';

interface SEOProps {
    title: string;
    description?: string;
    schema?: any;
}

export default function SEO({ title, description, schema }: SEOProps) {
    useEffect(() => {
        // Update title
        document.title = `${title} - Mẫu Văn Bản`;

        // Update meta description
        if (description) {
            let metaDesc = document.querySelector('meta[name="description"]');
            if (metaDesc) {
                metaDesc.setAttribute('content', description);
            } else {
                metaDesc = document.createElement('meta');
                metaDesc.setAttribute('name', 'description');
                metaDesc.setAttribute('content', description);
                document.head.appendChild(metaDesc);
            }
        }

        // Handle JSON-LD Schema
        if (schema) {
            const scriptId = 'json-ld-schema';
            const existingScript = document.getElementById(scriptId) as HTMLScriptElement | null;

            if (existingScript) {
                existingScript.innerHTML = JSON.stringify(schema);
            } else {
                const script = document.createElement('script');
                script.id = scriptId;
                script.type = 'application/ld+json';
                script.innerHTML = JSON.stringify(schema);
                document.head.appendChild(script);
            }
        }

        return () => {
            // Optional: clean up script on unmount
            const script = document.getElementById('json-ld-schema');
            if (script) script.remove();
        };
    }, [title, description, schema]);

    return null;
}
