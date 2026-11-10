import {useState} from 'react'
import Header from './components/Header'
import Login from './pages/Login'
import StudentDashboard from './pages/StudentDashboard'
export default function App(){const [session,setSession]=useState(null);return <main className="container"><Header user={session?.name} onLogout={()=>setSession(null)}/>{session?<StudentDashboard session={session}/>:<Login onLogin={setSession}/>}<footer>FinPay academic project · local educational prototype only</footer></main>}
