import axios from 'axios';

const api = axios.create({
    baseURL: 'https://chemical-equipment-visualizer-wptm.onrender.com/api/',
    auth: {
        username: 'admin', 
        email: 'admin@gmail.com',  
        password: 'ravi_admin@123'
    }
});

export default api;