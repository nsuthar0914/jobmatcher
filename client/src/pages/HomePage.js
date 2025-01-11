import { Box, Button, TextField, Typography } from '@mui/material';
import React, { useState } from 'react';
import Visualization from '../components/Visualization';

function HomePage() {
    const [entityId, setEntityId] = useState('');
    const [showGraph, setShowGraph] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        setShowGraph(true);
    };

    return (
        <Box sx={{ p: 4, maxWidth: 600, margin: '0 auto', boxShadow: 3, borderRadius: 2 }}>
            <Typography variant="h4" gutterBottom>Similarity Graph Viewer</Typography>
            <form onSubmit={handleSubmit}>
                <TextField
                    fullWidth
                    label="Entity ID (UUID)"
                    variant="outlined"
                    margin="normal"
                    value={entityId}
                    onChange={(e) => setEntityId(e.target.value)}
                    required
                />
                <Button type="submit" variant="contained" color="primary" fullWidth>
                    View Visualization
                </Button>
            </form>
            {showGraph && <Visualization entityId={entityId} />}
        </Box>
    );
}

export default HomePage;
