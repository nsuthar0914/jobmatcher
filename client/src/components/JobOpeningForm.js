import { Box, Button, Grid, TextField, Typography } from '@mui/material';
import axios from 'axios';
import React, { useState } from 'react';

function JobOpeningForm() {
    const [formData, setFormData] = useState({
        creator_email: '',
        job_title: '',
        company_name: '',
        job_description: '',
        company_values: '',
        team_structure: '',
        growth_opportunities: '',
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('https://job-matching-api.onrender.com/job-opening/create', formData);
            alert(`Job ID: ${response.data.job_id}`);
        } catch (error) {
            console.error(error);
            alert('Failed to create job opening.');
        }
    };

    return (
        <Box sx={{ p: 4, maxWidth: 600, margin: '0 auto', boxShadow: 3, borderRadius: 2 }}>
            <Typography variant="h4" gutterBottom>Create Job Opening</Typography>
            <form onSubmit={handleSubmit}>
                <TextField
                    fullWidth
                    label="Creator Email"
                    variant="outlined"
                    margin="normal"
                    required
                    onChange={(e) => setFormData({ ...formData, creator_email: e.target.value })}
                />
                <TextField
                    fullWidth
                    label="Job Title"
                    variant="outlined"
                    margin="normal"
                    required
                    onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
                />
                <TextField
                    fullWidth
                    label="Company Name"
                    variant="outlined"
                    margin="normal"
                    required
                    onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                />
                <TextField
                    fullWidth
                    label="Job Description"
                    variant="outlined"
                    multiline
                    rows={4}
                    margin="normal"
                    required
                    onChange={(e) => setFormData({ ...formData, job_description: e.target.value })}
                />
                <TextField
                    fullWidth
                    label="Company Values"
                    variant="outlined"
                    multiline
                    rows={3}
                    margin="normal"
                    required
                    onChange={(e) => setFormData({ ...formData, company_values: e.target.value })}
                />
                <TextField
                    fullWidth
                    label="Team Structure"
                    variant="outlined"
                    multiline
                    rows={3}
                    margin="normal"
                    required
                    onChange={(e) => setFormData({ ...formData, team_structure: e.target.value })}
                />
                <TextField
                    fullWidth
                    label="Growth Opportunities"
                    variant="outlined"
                    multiline
                    rows={3}
                    margin="normal"
                    required
                    onChange={(e) => setFormData({ ...formData, growth_opportunities: e.target.value })}
                />
                <Grid container justifyContent="flex-end" sx={{ mt: 3 }}>
                    <Button type="submit" variant="contained" color="primary">Submit</Button>
                </Grid>
            </form>
        </Box>
    );
}

export default JobOpeningForm;
