import { Box, Button, Grid, Input, TextField, Typography } from '@mui/material';
import axios from 'axios';
import React, { useState } from 'react';

function JobSeekerForm() {
    const [formData, setFormData] = useState({ email: '', linkedin_url: '', github_url: '' });
    const [resume, setResume] = useState(null);
    const [coverLetter, setCoverLetter] = useState(null);
    const [certificates, setCertificates] = useState([]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const data = new FormData();
        Object.keys(formData).forEach((key) => data.append(key, formData[key]));
        data.append('resume', resume);
        if (coverLetter) data.append('cover_letter', coverLetter);
        certificates.forEach((file, index) => data.append(`certificates[${index}]`, file));

        try {
            const response = await axios.post('https://job-matching-api.onrender.com/job-seeker/upload', data);
            alert(`Seeker ID: ${response.data.seeker_id}`);
        } catch (error) {
            console.error(error);
            alert('Failed to upload.');
        }
    };

    return (
        <Box sx={{ p: 4, maxWidth: 600, margin: '0 auto', boxShadow: 3, borderRadius: 2 }}>
            <Typography variant="h4" gutterBottom>Job Seeker Profile Upload</Typography>
            <form onSubmit={handleSubmit}>
                <TextField
                    fullWidth
                    label="Email"
                    variant="outlined"
                    margin="normal"
                    required
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
                <TextField
                    fullWidth
                    label="LinkedIn URL"
                    variant="outlined"
                    margin="normal"
                    onChange={(e) => setFormData({ ...formData, linkedin_url: e.target.value })}
                />
                <TextField
                    fullWidth
                    label="GitHub URL"
                    variant="outlined"
                    margin="normal"
                    onChange={(e) => setFormData({ ...formData, github_url: e.target.value })}
                />
                <Typography variant="subtitle1" sx={{ mt: 2 }}>Upload Resume (PDF)</Typography>
                <Input type="file" required onChange={(e) => setResume(e.target.files[0])} />
                <Typography variant="subtitle1" sx={{ mt: 2 }}>Upload Cover Letter (Optional)</Typography>
                <Input type="file" onChange={(e) => setCoverLetter(e.target.files[0])} />
                <Typography variant="subtitle1" sx={{ mt: 2 }}>Upload Certificates (Optional)</Typography>
                <Input type="file" multiple onChange={(e) => setCertificates([...e.target.files])} />
                <Grid container justifyContent="flex-end" sx={{ mt: 3 }}>
                    <Button type="submit" variant="contained" color="primary">Submit</Button>
                </Grid>
            </form>
        </Box>
    );
}

export default JobSeekerForm;
