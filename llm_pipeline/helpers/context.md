Your task is to read the markdown-parsed content of a scholarly paper and output a **complete, structured JSON object** describing the publication's related project and funding (if any).

Follow these principles:

1. **Extract only factual information present in the paper.**

   * Do not infer or fabricate missing data.
   * If something cannot be found, set its value to `null`.
   * If you are unsure about a value, use `null` rather than guessing.

2. **Identify project and funding information.**

   * From acknowledgements or funding statements, extract:

     * projectName: The names or codes of grants or projects.
     * fundingOrgAgency: The funding programme, organisation/agency, or scheme names (e.g. “Horizon 2020”, “NWA”).
     * grantNumber: Any grant or project identifiers, numbers, or acronyms.
     * resultType: The type of of research output.
     * If multiple funders or grants are mentioned, include all of them.

3. **Consistency.**
   * When extracting complex fields like project names or funding details, prefer the version as written (verbatim text).
   * Preserve identifiers (e.g., “GA-123456”, “H2020-MSCA-IF-2020”) exactly as they appear.
   * Avoid verbose information, prefer minimal, short identifiers (e.g. for a grantNumber, only output the number/id; for affiliation, output the full, unambiguous name of the institution, but avoid adding its full address)

4. **Glossary**

    Below are some context-specific terms that might be relevant for parsing the documents:
    
   * Nederlandse Organisatie voor Wetenschappelijk Onderzoek (NWO): Dutch Research Council - the national research council of the Netherlands. NWO funds thousands of top researchers at universities and institutes and steers the course of Dutch science by means of subsidies and research programmes.  

   NWO Financieringslijnen | Financing lines (in Dutch):
   1. Open Competitie - Nieuwsgierigheidsgedreven onderzoek 
   2. Talentprogramma - Nieuwsgierigheidsgedreven ongebonden onderzoek gericht op onderzoekstalent 
   3. Kennis- en Innovatieconvenant (KIC) - Projecten of programma's in samenwerking met externe publieke en/of private partijen 
   4. Nationale Wetenschapsagenda (NWA) - Bevorderen dat wetenschap bijdraagt aan maatschappelijke en economische uitdagingen 
   5. Wetenschappelijke infrastructuur - Realiseren van grootschalige infrastructuur
   
Your final output must represent all the identifiable bibliographic and funding information in structured form, with every field included and unfilled ones explicitly marked as `null`.