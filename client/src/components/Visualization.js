import axios from 'axios';
import React, { useEffect, useState } from 'react';

function Visualization({ entityId }) {
    const [imageUrl, setImageUrl] = useState('');
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchVisualization = async () => {
            try {
                const response = await axios.get(`https://job-matching-api.onrender.com/visualization/${entityId}`, {
                    responseType: 'blob', // Important for file responses
                });
                const url = URL.createObjectURL(new Blob([response.data]));
                setImageUrl(url);
            } catch (err) {
                setError('Failed to load visualization.');
            }
        };

        fetchVisualization();
    }, [entityId]);

    if (error) return <p>{error}</p>;
    if (!imageUrl) return <p>Loading visualization...</p>;

    return (
        <div>
            <h1>Similarity Graph</h1>
            <img src={imageUrl} alt="Similarity Graph" style={{ width: '100%' }} />
        </div>
    );
}

export default Visualization;
