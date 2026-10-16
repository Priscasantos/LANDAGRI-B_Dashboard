import { useState } from 'react';
import {
  Compass,
  ExternalLink,
  Globe,
  Mail,
  Map as MapIcon,
  Quote,
  Search,
  Wheat,
  type LucideIcon,
} from 'lucide-react';
import AnimatedPage from '../components/AnimatedPage';
import { getBasename } from '../config/routes';
import { useT } from '../i18n/LanguageContext';

const DOI_SANTOS_2025 = 'https://doi.org/10.3390/rs17132324';
const URL_CONAB = 'https://www.conab.gov.br/';
const URL_IBGE = 'https://www.ibge.gov.br/';
const URL_SID_SANTOS_ADAMI =
  'http://mtc-m16c.sid.inpe.br/ibi/sid.inpe.br/mtc-m18/2010/10.19.13.42?ibiurl.clientinformation.citingitem=sid.inpe.br/mtc-m18/2010/12.15.11.49&linktype=relative';
const URL_ZENODO = 'https://doi.org/10.5281/zenodo.17042299';
const CONTACT_EMAIL = 'priscilla.santos@inpe.br';
const URL_GITHUB = 'https://github.com/landagri-b';

/** Logos institucionais servidos sob o basename do router (sub-path gh-pages). */
function logoUrl(file: string): string {
  const base = getBasename().replace(/\/+$/, '');
  return `${base}/logos/${file}`;
}

interface PartnerLogoProps {
  src: string;
  alt: string;
  fallbackLabel: string;
}

/**
 * Logo com fallback acessível: se o asset não existir, renderiza um
 * placeholder com o mesmo `alt` em vez de uma imagem quebrada.
 */
function PartnerLogo({ src, alt, fallbackLabel }: PartnerLogoProps): React.JSX.Element {
  const [failed, setFailed] = useState(false);

  if (failed) {
    return (
      <div
        role="img"
        aria-label={alt}
        className="mx-auto flex h-24 w-full max-w-75 items-center justify-center rounded-xl border border-dashed border-border bg-canvas px-4 text-center text-xs text-fg-muted"
      >
        {fallbackLabel}
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      width={300}
      loading="lazy"
      onError={(): void => setFailed(true)}
      className="mx-auto h-auto max-h-24 w-auto max-w-full object-contain"
    />
  );
}

interface SectionHeadingProps {
  icon: LucideIcon;
  title: string;
  id: string;
}

function SectionHeading({ icon: Icon, title, id }: SectionHeadingProps): React.JSX.Element {
  return (
    <h2
      id={id}
      className="flex items-center gap-2 text-lg font-bold tracking-tight text-fg"
    >
      <Icon size={20} aria-hidden="true" className="shrink-0 text-primary" />
      {title}
    </h2>
  );
}

const EXTERNAL_LINK_CLASS =
  'font-medium text-primary underline decoration-primary/40 underline-offset-2 hover:decoration-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary';

interface ExternalRefProps {
  href: string;
  children: string;
}

function ExternalRef({ href, children }: ExternalRefProps): React.JSX.Element {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className={EXTERNAL_LINK_CLASS}>
      {children}
    </a>
  );
}

/**
 * Página institucional — espelha `dashboard/about.py` (Streamlit legado).
 * Sem exports CSV/JSON e sem Technical Metadata (fora do escopo do antigo);
 * `src/lib/dataExport` permanece intacto para os demais módulos.
 */
export default function AboutPage(): React.JSX.Element {
  const { t } = useT('about');
  const { t: tNav } = useT('nav');

  const moduleCards = [
    {
      icon: Search,
      title: t('cardOverviewTitle'),
      text: t('cardOverviewText'),
      accent: 'border-l-primary',
    },
    {
      icon: MapIcon,
      title: t('cardInitiativeTitle'),
      text: t('cardInitiativeText'),
      accent: 'border-l-[#8B4513]',
    },
  ];

  return (
    <AnimatedPage>
      <div className="space-y-6">
        <p className="max-w-4xl text-sm leading-relaxed text-fg-secondary md:text-base">
          <strong className="text-fg">{t('introLead')}</strong> {t('introA')}{' '}
          <em>{tNav('overview')}</em>, <em>{tNav('initiativeAnalysis')}</em> {t('introAnd')}{' '}
          <em>{tNav('agriculturalAnalysis')}</em>
          {t('introPlus')} <em>{tNav('about')}</em>
          {t('introModuleSuffix')} {t('introEnd')}
        </p>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="space-y-4">
            {moduleCards.map((card) => {
              const CardIcon = card.icon;
              return (
                <section
                  key={card.title}
                  aria-label={card.title}
                  className={`rounded-xl border border-border border-l-4 bg-card p-5 ${card.accent}`}
                >
                  <h2 className="flex items-center gap-2 text-base font-bold text-fg">
                    <CardIcon size={18} aria-hidden="true" className="shrink-0 text-primary" />
                    {card.title}
                  </h2>
                  <p className="mt-2 text-sm leading-relaxed text-fg-secondary">{card.text}</p>
                </section>
              );
            })}
          </div>
          <section
            aria-label={t('cardAgriTitle')}
            className="rounded-xl border border-border border-l-4 border-l-terra-fill bg-card p-5"
          >
            <h2 className="flex items-center gap-2 text-base font-bold text-fg">
              <Wheat size={18} aria-hidden="true" className="shrink-0 text-primary" />
              {t('cardAgriTitle')}
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-fg-secondary">{t('cardAgriText')}</p>
          </section>
        </div>

        <section
          aria-labelledby="about-navigate"
          className="rounded-xl border border-border border-l-4 border-l-primary bg-card p-5"
        >
          <SectionHeading icon={Compass} title={t('navigateTitle')} id="about-navigate" />
          <ul className="mt-3 list-disc space-y-1.5 pl-6 text-sm leading-relaxed text-fg-secondary">
            <li>{t('navigateBullet1')}</li>
            <li>{t('navigateBullet2')}</li>
            <li>{t('navigateBullet3')}</li>
          </ul>
        </section>

        <section
          aria-labelledby="about-sources"
          className="rounded-xl border border-border bg-card p-5"
        >
          <SectionHeading icon={Globe} title={t('sourcesTitle')} id="about-sources" />
          <ul className="mt-3 list-disc space-y-1.5 pl-6 text-sm leading-relaxed text-fg-secondary">
            <li>
              {t('sourcesLulcPre')} <ExternalRef href={DOI_SANTOS_2025}>{t('sourcesSantos')}</ExternalRef>.
            </li>
            <li>
              {t('sourcesAgriPre')} <ExternalRef href={URL_CONAB}>CONAB</ExternalRef>{' '}
              {t('sourcesAnd')} <ExternalRef href={URL_IBGE}>IBGE</ExternalRef>.
            </li>
          </ul>
        </section>

        <section
          aria-labelledby="about-citation"
          className="rounded-xl border border-border bg-card p-5"
        >
          <SectionHeading icon={Quote} title={t('citationTitle')} id="about-citation" />
          <p className="mt-3 text-sm leading-relaxed text-fg-secondary">{t('citationLicense')}</p>
          <p className="mt-2 text-sm leading-relaxed text-fg-secondary">{t('citationAuth')}</p>
          <p className="mt-2 text-sm leading-relaxed text-fg-secondary">{t('citationIntro')}</p>
          <ul className="mt-2 list-disc space-y-1.5 pl-6 text-sm leading-relaxed text-fg-secondary">
            <li>
              {t('citationMainArticle')}{' '}
              <ExternalRef href={DOI_SANTOS_2025}>{t('refSantosMain')}</ExternalRef>.
            </li>
            <li>
              {t('citationProjectArticle')}{' '}
              <ExternalRef href={URL_SID_SANTOS_ADAMI}>{t('refSantosAdami')}</ExternalRef>.
            </li>
            <li>
              {t('citationZenodo')}{' '}
              <ExternalRef href={URL_ZENODO}>{t('refZenodo')}</ExternalRef>.
            </li>
          </ul>
        </section>

        <section
          aria-labelledby="about-contact"
          className="rounded-xl border border-border bg-card p-5"
        >
          <SectionHeading icon={Mail} title={t('contactTitle')} id="about-contact" />
          <p className="mt-3 text-sm leading-relaxed text-fg-secondary">{t('contactIntro')}</p>
          <ul className="mt-2 space-y-1.5 text-sm leading-relaxed text-fg-secondary">
            <li className="flex flex-wrap items-center gap-x-2">
              <span className="font-semibold text-fg">{t('contactEmailLabel')}</span>
              <a href={`mailto:${CONTACT_EMAIL}`} className={EXTERNAL_LINK_CLASS}>
                {CONTACT_EMAIL}
              </a>
              <span>{t('contactHeadSuffix')}</span>
            </li>
            <li className="flex flex-wrap items-center gap-x-2">
              <span className="font-semibold text-fg">{t('contactGithubLabel')}</span>
              <a
                href={URL_GITHUB}
                target="_blank"
                rel="noopener noreferrer"
                className={`inline-flex items-center gap-1 ${EXTERNAL_LINK_CLASS}`}
              >
                {URL_GITHUB}
                <ExternalLink size={12} aria-hidden="true" />
              </a>
            </li>
          </ul>
        </section>

        <section
          aria-label={t('logosLabel')}
          className="rounded-xl border border-border bg-card p-5"
        >
          <div className="grid grid-cols-1 items-center gap-6 sm:grid-cols-3">
            <PartnerLogo
              src={logoUrl('INPE.png')}
              alt={t('logoInpeAlt')}
              fallbackLabel={t('logoMissing')}
            />
            <PartnerLogo
              src={logoUrl('AGRIRSLAB.png')}
              alt={t('logoAgrirslabAlt')}
              fallbackLabel={t('logoMissing')}
            />
            <PartnerLogo
              src={logoUrl('LANDAGRIB.png')}
              alt={t('logoLandagribAlt')}
              fallbackLabel={t('logoMissing')}
            />
          </div>
        </section>
      </div>
    </AnimatedPage>
  );
}
