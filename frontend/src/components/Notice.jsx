export default function Notice({message, error}) { return message ? <div className={`notice ${error ? 'error' : ''}`}>{message}</div> : null }
