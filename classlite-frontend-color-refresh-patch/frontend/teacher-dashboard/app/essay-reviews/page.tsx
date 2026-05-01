"use client";

export default function EssayReviewsPage() {
  const items = [
    {
      review_id: 1,
      prompt: "Explain the difference between Moore and Mealy machines.",
      answer: "A Moore machine depends only on state while a Mealy machine depends on state and input.",
      proposed_score: 8,
      confidence: 0.82,
      max_marks: 10,
    },
  ];

  return (
    <main>
      <h1 className="page-title">Essay Review Queue</h1>
      <p className="page-subtitle">Approve, revise, and publish AI-assisted grading decisions.</p>

      {items.map((item) => (
        <section key={item.review_id} className="card card-accent">
          <h2 className="card-title">Review #{item.review_id}</h2>
          <div className="kv"><strong>Question:</strong> {item.prompt}</div>
          <div className="kv"><strong>Student answer:</strong> {item.answer}</div>
          <div className="kv"><strong>AI proposed score:</strong> {item.proposed_score} / {item.max_marks}</div>
          <div className="kv"><strong>Confidence:</strong> {item.confidence}</div>
          <div className="button-row">
            <button className="btn btn-success">Approve</button>
            <button className="btn btn-warning">Adjust Score</button>
            <button className="btn btn-secondary">Skip</button>
          </div>
        </section>
      ))}
    </main>
  );
}
