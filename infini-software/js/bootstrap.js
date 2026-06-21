import axios from 'axios';
window.axios = axios;
// import { initializeApp } from 'firebase/app';
// import { getFirestore } from "firebase/firestore";
// // import { getDatabase } from 'firebase/database';
// import { getDatabase, ref, onValue, query, orderByChild } from 'firebase/database';
// // const db = firebase.firestore();

// // TODO: Replace the following with your app's Firebase project configuration
// const firebaseConfig = {
//     authDomain: "kikip-a63be.firebaseapp.com",
//     apiKey: 'AIzaSyAqcOoaC9w8XIvCyNChFCtLsJsD9uNmdkw',
//     databaseURL: "https://kikip-a63be-default-rtdb.firebaseio.com",
//     storageBucket: "kikip-a63be.firebasestorage.app",

//     messagingSenderId: '1041564433832',
//     projectId: 'kikip-a63be',
//     appId: '1:1041564433832:android:76051c5afdf2f26b97b19d',
// };

// const app = initializeApp(firebaseConfig);
// const database = getDatabase(app);

// // export { database };
// export { database, ref, onValue, query, orderByChild };
// // const db = getFirestore(app);

window.axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
