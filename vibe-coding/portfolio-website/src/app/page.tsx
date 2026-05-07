"use client";

import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  BarChart3,
  Globe,
  ShieldCheck,
  Database,
  Users,
  TrendingUp,
  Mail,
} from "lucide-react";

const fadeInUp = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
};

const staggerContainer = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.15 } },
};

const services = [
  {
    icon: <Database className="h-8 w-8 text-blue-400" />,
    title: "Data Engineering",
    description:
      "Design and build robust data pipelines, ETL workflows, and scalable data infrastructure that powers analytics at any scale.",
  },
  {
    icon: <BarChart3 className="h-8 w-8 text-purple-400" />,
    title: "Data Analytics",
    description:
      "Transform raw data into actionable insights through advanced analytics, dashboards, and meaningful visualizations.",
  },
  {
    icon: <TrendingUp className="h-8 w-8 text-emerald-400" />,
    title: "Machine Learning",
    description:
      "Build predictive models and deploy ML solutions that drive real business value and automate complex decisions.",
  },
  {
    icon: <Globe className="h-8 w-8 text-cyan-400" />,
    title: "Cloud Solutions",
    description:
      "Architect and deploy cloud-native data platforms on AWS, GCP, and Azure for maximum reliability and scalability.",
  },
  {
    icon: <ShieldCheck className="h-8 w-8 text-green-400" />,
    title: "Data Governance",
    description:
      "Establish data quality standards, lineage tracking, and governance frameworks that ensure trustworthy data assets.",
  },
  {
    icon: <Users className="h-8 w-8 text-orange-400" />,
    title: "Team Enablement",
    description:
      "Coach data teams, establish best practices, and build self-serve analytics cultures across your organization.",
  },
];

const stats = [
  { label: "Projects Delivered", value: "50+" },
  { label: "TB of Data Processed", value: "200+" },
  { label: "Years Experience", value: "8+" },
  { label: "Happy Clients", value: "30+" },
];

export default function PortfolioWebsite() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 font-sans">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-gray-950/80 backdrop-blur-md border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <span className="text-xl font-bold text-blue-400">Alex Rivera</span>
          <div className="hidden md:flex items-center gap-8 text-sm text-gray-400">
            <a href="#services" className="hover:text-white transition-colors">Services</a>
            <a href="#about" className="hover:text-white transition-colors">About</a>
            <a href="#contact" className="hover:text-white transition-colors">Contact</a>
          </div>
          <Button
            className="bg-blue-600 hover:bg-blue-500 text-white text-sm px-4 py-2 rounded-lg"
            onClick={() => document.getElementById("contact")?.scrollIntoView({ behavior: "smooth" })}
          >
            Hire Me
          </Button>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-950 via-gray-950 to-purple-950 opacity-80" />
        <div className="absolute inset-0">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute rounded-full bg-blue-500/10"
              style={{
                width: `${Math.random() * 300 + 50}px`,
                height: `${Math.random() * 300 + 50}px`,
                top: `${Math.random() * 100}%`,
                left: `${Math.random() * 100}%`,
                filter: "blur(60px)",
              }}
            />
          ))}
        </div>
        <motion.div
          className="relative z-10 text-center px-6 max-w-4xl mx-auto"
          initial="hidden"
          animate="visible"
          variants={staggerContainer}
        >
          <motion.div variants={fadeInUp} className="mb-4">
            <span className="inline-block px-4 py-1.5 rounded-full text-sm font-medium bg-blue-500/20 text-blue-300 border border-blue-500/30">
              Data Scientist & Data Engineer
            </span>
          </motion.div>
          <motion.h1
            variants={fadeInUp}
            className="text-5xl md:text-7xl font-extrabold mb-6 bg-gradient-to-r from-white via-blue-200 to-purple-300 bg-clip-text text-transparent leading-tight"
          >
            Alex Rivera
          </motion.h1>
          <motion.p
            variants={fadeInUp}
            className="text-xl md:text-2xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed"
          >
            I turn complex data into clear decisions — building pipelines,
            models, and analytics platforms that scale.
          </motion.p>
          <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              className="bg-blue-600 hover:bg-blue-500 text-white text-lg px-8 py-6 rounded-xl font-semibold shadow-lg shadow-blue-500/25 transition-all"
              onClick={() => document.getElementById("services")?.scrollIntoView({ behavior: "smooth" })}
            >
              View My Work
            </Button>
            <Button
              className="border border-gray-600 bg-transparent hover:bg-gray-800 text-gray-200 text-lg px-8 py-6 rounded-xl font-semibold transition-all"
              onClick={() => document.getElementById("contact")?.scrollIntoView({ behavior: "smooth" })}
            >
              <Mail className="mr-2 h-5 w-5" />
              Get in Touch
            </Button>
          </motion.div>
        </motion.div>
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce text-gray-600">
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </section>

      {/* Services */}
      <section id="services" className="py-24 px-6 max-w-6xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
        >
          <motion.div variants={fadeInUp} className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-white">What I Do</h2>
            <p className="text-gray-400 text-lg max-w-xl mx-auto">
              End-to-end data expertise from raw ingestion to production-ready insights.
            </p>
          </motion.div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {services.map((service) => (
              <motion.div key={service.title} variants={fadeInUp}>
                <Card className="bg-gray-900 border-gray-800 hover:border-blue-500/50 transition-all duration-300 hover:-translate-y-1 h-full">
                  <CardContent className="p-6 pt-6">
                    <div className="mb-4 p-3 rounded-xl bg-gray-800 w-fit">
                      {service.icon}
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-2">{service.title}</h3>
                    <p className="text-gray-400 text-sm leading-relaxed">{service.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* About / Stats */}
      <section id="about" className="py-24 px-6 bg-gray-900/50">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
            className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center"
          >
            <motion.div variants={fadeInUp}>
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 mb-6">
                <TrendingUp className="h-4 w-4" /> About Me
              </span>
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
                Turning Data Into <span className="text-blue-400">Competitive Advantage</span>
              </h2>
              <p className="text-gray-400 text-lg leading-relaxed mb-6">
                With 8+ years of experience across fintech, e-commerce, and healthcare, I specialize
                in designing data systems that are not just fast — but reliable, maintainable, and
                business-aligned.
              </p>
              <p className="text-gray-400 text-lg leading-relaxed mb-8">
                From Apache Spark pipelines processing hundreds of terabytes to lightweight Python
                scripts that save teams hours every week, I love solving data problems at every scale.
              </p>
              <div className="flex flex-wrap gap-2">
                {["Python", "SQL", "Spark", "dbt", "Airflow", "Kafka", "AWS", "Terraform", "PyTorch"].map(
                  (tech) => (
                    <span
                      key={tech}
                      className="px-3 py-1 rounded-full text-sm bg-gray-800 text-gray-300 border border-gray-700"
                    >
                      {tech}
                    </span>
                  )
                )}
              </div>
            </motion.div>
            <motion.div variants={staggerContainer} className="grid grid-cols-2 gap-6">
              {stats.map((stat) => (
                <motion.div key={stat.label} variants={fadeInUp}>
                  <Card className="bg-gray-900 border-gray-800 text-center p-6">
                    <CardContent className="p-0">
                      <div className="text-4xl font-extrabold text-blue-400 mb-2">{stat.value}</div>
                      <div className="text-gray-400 text-sm">{stat.label}</div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Contact */}
      <section id="contact" className="py-24 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp}>
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-500/20 border border-blue-500/30 mb-8">
                <Mail className="h-8 w-8 text-blue-400" />
              </div>
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                Let&apos;s Work Together
              </h2>
              <p className="text-gray-400 text-lg mb-10 leading-relaxed">
                Have a data challenge you&apos;d like to solve? I&apos;m open to freelance projects,
                consulting engagements, and full-time opportunities.
              </p>
            </motion.div>
            <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button className="bg-blue-600 hover:bg-blue-500 text-white text-lg px-8 py-6 rounded-xl font-semibold shadow-lg shadow-blue-500/25">
                <Mail className="mr-2 h-5 w-5" />
                alex@example.com
              </Button>
              <Button className="border border-gray-600 bg-transparent hover:bg-gray-800 text-gray-200 text-lg px-8 py-6 rounded-xl font-semibold">
                View LinkedIn
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 px-6 text-center text-gray-600 text-sm">
        <p>© {new Date().getFullYear()} Alex Rivera · Built with Next.js & Tailwind CSS</p>
      </footer>
    </div>
  );
}
