import Link from "next/link";

export default function Home() {
  return (
    <main>
      <div className="card">
        <h1>Formal Exam Client</h1>
        <p className="muted">Open the formal exam runner to start a session.</p>
        <Link href="/formal-runner">Go to Formal Runner</Link>
      </div>
    </main>
  );
}
