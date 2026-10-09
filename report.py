def build_html(jobs):
    rows = []
    for job in jobs:
        rows.append(f"""
        <tr>
          <td>{job.get('title', '')}</td>
          <td>{job.get('company', '')}</td>
          <td>{job.get('location', '')}</td>
          <td>{job.get('salary', '')}</td>
          <td>{job.get('score', '')}</td>
          <td><a href="{job.get('url', '')}" target="_blank">View</a></td>
        </tr>
        """)

    rows_html = "\n".join(rows)

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h1>Daily Job Scan Results</h1>
        <p>Here are the jobs that passed filters and scored above your threshold.</p>

        <table border="1" cellspacing="0" cellpadding="6" style="border-collapse: collapse; width: 100%;">
          <tr style="background-color: #f2f2f2;">
            <th>Title</th>
            <th>Company</th>
            <th>Location</th>
            <th>Salary</th>
            <th>Score</th>
            <th>Link</th>
          </tr>
          {rows_html}
        </table>

        <br><br>
        <p style="color: #777;">Generated automatically by your Job Scanner.</p>
      </body>
    </html>
    """
