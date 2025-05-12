import React, { useEffect, useState } from 'react';
import { getData } from '../apis/tempAPI';

const HomePage = () => {
    const [data, setData] = useState('');

    useEffect(() => {
        getData().then((response) => setData(response.data.message));
    }, []);

    return <div>{data || 'Loading...'}</div>;
};

export default HomePage;