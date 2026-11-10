import {useState} from 'react'
import {api} from '../api'
import Notice from '../components/Notice'
export default function Login({onLogin}) {
 const [email,setEmail]=useState('rahul@finpay.local'), [password,setPassword]=useState('Student@123'), [message,setMessage]=useState('')
 async function submit(e){e.preventDefault();setMessage('');try{const data=await api('/auth/login',{method:'POST',body:JSON.stringify({email,password})});if(data.role!=='STUDENT')throw new Error('Use a student account for the wallet dashboard.');onLogin(data)}catch(err){setMessage(err.message)}}
 return <section className="panel login"><h2>Student login</h2><p className="muted">Demo: rahul@finpay.local / Student@123</p><form onSubmit={submit}><label>Email<input type="email" value={email} onChange={e=>setEmail(e.target.value)} required/></label><label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} required/></label><button className="button full">Sign in</button></form><Notice message={message} error/></section>
}
