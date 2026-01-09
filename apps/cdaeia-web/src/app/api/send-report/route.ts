import { NextRequest, NextResponse } from 'next/server';
import { Resend } from 'resend';

// Initialize Resend only if API key is available
const resend = process.env.RESEND_API_KEY ? new Resend(process.env.RESEND_API_KEY) : null;

interface SendReportRequest {
  email: string;
  companyName: string;
  result: {
    totalScore: number;
    maxScore: number;
    percentage: number;
    eligibilityStatus: string;
    statusMessage: string;
    creditCurrent: { totalCredit: number } | null;
    creditOptimized: { totalCredit: number } | null;
    creditGain: number;
  };
}

export async function POST(request: NextRequest) {
  try {
    // Check if Resend is configured
    if (!resend) {
      console.warn('RESEND_API_KEY not configured - email sending disabled');
      return NextResponse.json(
        { error: 'Service d\'email non configure. Contactez info@ran-ai-agency.ca pour recevoir votre rapport.' },
        { status: 503 }
      );
    }

    const body: SendReportRequest = await request.json();
    const { email, companyName, result } = body;

    // Validate email
    if (!email || !email.includes('@')) {
      return NextResponse.json(
        { error: 'Email invalide' },
        { status: 400 }
      );
    }

    // Format currency
    const formatCurrency = (amount: number) =>
      new Intl.NumberFormat('fr-CA', {
        style: 'currency',
        currency: 'CAD',
        minimumFractionDigits: 0,
      }).format(amount);

    // Determine status emoji and color
    const statusEmoji =
      result.eligibilityStatus === 'eligible'
        ? '✅'
        : result.eligibilityStatus === 'partial'
        ? '⚠️'
        : '❌';

    const statusLabel =
      result.eligibilityStatus === 'eligible'
        ? 'ELIGIBLE'
        : result.eligibilityStatus === 'partial'
        ? 'PARTIELLEMENT ELIGIBLE'
        : 'NON ELIGIBLE';

    // Send email to client
    // IMPORTANT: With onboarding@resend.dev (test domain), emails can only be sent
    // to the email address associated with the Resend account.
    // To send to any email, verify ran-ai-agency.ca at https://resend.com/domains
    console.log(`Attempting to send email to: ${email}`);

    const { data, error } = await resend.emails.send({
      from: 'Ran.AI Agency <onboarding@resend.dev>',
      to: [email],
      subject: `Votre diagnostic CDAEIA - ${companyName}`,
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
          <div style="background: linear-gradient(135deg, #2563eb, #4f46e5); padding: 30px; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">Ran.AI Agency</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">Diagnostic CDAEIA</p>
          </div>

          <div style="background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; border-top: none;">
            <h2 style="margin-top: 0;">Bonjour,</h2>

            <p>Merci d'avoir complete le diagnostic CDAEIA pour <strong>${companyName}</strong>.</p>

            <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb; margin: 20px 0;">
              <h3 style="margin-top: 0; color: #1f2937;">Resultats du diagnostic</h3>

              <table style="width: 100%; border-collapse: collapse;">
                <tr>
                  <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">Score</td>
                  <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: bold;">
                    ${result.totalScore}/${result.maxScore} (${Math.round(result.percentage)}%)
                  </td>
                </tr>
                <tr>
                  <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">Statut</td>
                  <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: bold;">
                    ${statusEmoji} ${statusLabel}
                  </td>
                </tr>
                <tr>
                  <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">Credit actuel estime</td>
                  <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: bold; color: #2563eb;">
                    ${result.creditCurrent ? formatCurrency(result.creditCurrent.totalCredit) : 'N/A'}/an
                  </td>
                </tr>
                <tr>
                  <td style="padding: 10px 0;">Credit optimise potentiel</td>
                  <td style="padding: 10px 0; text-align: right; font-weight: bold; color: #16a34a;">
                    ${result.creditOptimized ? formatCurrency(result.creditOptimized.totalCredit) : 'N/A'}/an
                  </td>
                </tr>
              </table>

              ${
                result.creditGain > 0
                  ? `
                  <div style="background: #dcfce7; padding: 15px; border-radius: 5px; margin-top: 15px; text-align: center;">
                    <strong style="color: #166534;">Gain potentiel: +${formatCurrency(result.creditGain)}/an</strong>
                  </div>
                  `
                  : ''
              }
            </div>

            <p>${result.statusMessage}</p>

            <h3>Prochaines etapes</h3>
            <ol>
              <li>Telechargez votre rapport PDF complet depuis l'application</li>
              <li>Revoyez les recommandations avec votre equipe</li>
              <li>Planifiez un appel de suivi gratuit avec nos experts</li>
            </ol>

            <div style="text-align: center; margin: 30px 0;">
              <a href="mailto:info@ran-ai-agency.ca?subject=Consultation%20CDAEIA%20-%20${encodeURIComponent(companyName)}"
                 style="background: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Demander une consultation gratuite
              </a>
            </div>
          </div>

          <div style="background: #1f2937; padding: 20px; border-radius: 0 0 10px 10px; text-align: center; color: white;">
            <p style="margin: 0 0 10px 0;"><strong>Ran.AI Agency</strong></p>
            <p style="margin: 0; font-size: 14px; color: rgba(255,255,255,0.8);">
              514-918-1241 | info@ran-ai-agency.ca | ran-ai-agency.ca
            </p>
          </div>
        </body>
        </html>
      `,
    });

    if (error) {
      console.error('Resend error:', error);
      // Check for test domain restriction
      if (error.message?.includes('not verified') || error.name === 'validation_error') {
        return NextResponse.json(
          {
            error: 'Le domaine d\'envoi n\'est pas encore verifie. Veuillez telecharger le PDF en attendant.',
            details: 'Pour recevoir les emails, le domaine ran-ai-agency.ca doit etre verifie dans Resend.'
          },
          { status: 503 }
        );
      }
      return NextResponse.json(
        { error: 'Erreur lors de l\'envoi de l\'email' },
        { status: 500 }
      );
    }

    console.log('Email sent successfully:', data?.id);

    // Also send notification to Ran.AI Agency
    // Note: Using Resend test domain until ran-ai-agency.ca is verified
    await resend.emails.send({
      from: 'CDAEIA Diagnostic <onboarding@resend.dev>',
      to: ['roland.ranaivo@sympatico.ca'], // Temporary until domain verified
      subject: `[LEAD] Nouveau diagnostic CDAEIA - ${companyName}`,
      html: `
        <h2>Nouveau diagnostic CDAEIA complete</h2>
        <table>
          <tr><td><strong>Entreprise:</strong></td><td>${companyName}</td></tr>
          <tr><td><strong>Email:</strong></td><td>${email}</td></tr>
          <tr><td><strong>Score:</strong></td><td>${result.totalScore}/${result.maxScore} (${Math.round(result.percentage)}%)</td></tr>
          <tr><td><strong>Statut:</strong></td><td>${statusLabel}</td></tr>
          <tr><td><strong>Credit actuel:</strong></td><td>${result.creditCurrent ? formatCurrency(result.creditCurrent.totalCredit) : 'N/A'}</td></tr>
          <tr><td><strong>Credit optimise:</strong></td><td>${result.creditOptimized ? formatCurrency(result.creditOptimized.totalCredit) : 'N/A'}</td></tr>
          <tr><td><strong>Gain potentiel:</strong></td><td>${formatCurrency(result.creditGain)}</td></tr>
        </table>
        <p><a href="mailto:${email}">Contacter le client</a></p>
      `,
    });

    return NextResponse.json({ success: true, id: data?.id });
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Une erreur est survenue' },
      { status: 500 }
    );
  }
}
