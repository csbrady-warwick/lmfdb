from flask import render_template, url_for
import siegel_core
import pickle
import urllib
from sage.all_cmdline import *

DATA = 'http://data.countnumber.de/Siegel-Modular-Forms/'
#DATA = '/media/data/home/nils/Sandbox/super_current/nilsskoruppa-lmfdb/db/'
#DATA = '/media/data/home/nils/Sandbox/super_current/Siegel-Modular-Forms/'

def render_webpage( args = {}):
    """
    Configure and return a template for the Siegel modular forms pages.
    """

    info = dict(args)
    info['learnmore'] = [ ('Siegel modular forms', 'http://en.wikipedia.org/wiki/Siegel_modular_form')]
    bread = [('Siegel modular forms', url_for( 'ModularForm_GSp4_Q_top_level'))]
    
    if len(args) == 0:
        return render_template("ModularForm_GSp4_Q/ModularForm_GSp4_Q_navigation.html", \
                               title = 'Siegel Modular Forms', \
                               bread = bread, \
                               **info)

    # possible keys for the URL
    group = args.get('group')
    character = args.get('character')
    weight = args.get('weight')
    level = args.get('level')
    form = args.get('form')
    page = args.get('page')
    orbit = args.get('orbit')
    weight_range = args.get('weight_range')
    modulus = args.get('modulus')

    # set info
    info['group'] = group
    info['form'] = form
    info['orbit']= orbit
    info['level']= level

    # We check first the key 'group' since it is needed always

    if args['group']:
        
        if 'Sp4Z' == args['group']:
            info['parent_as_tex'] = 'M_k\\big({\\rm Sp}(4,\\mathbb{Z})\\big)'
            dimension = siegel_core._dimension_Sp4Z
            info['generators'] = 'smf.Igusa_generators'

        elif 'Sp4Z_2' == args['group']:
            info['parent_as_tex'] = 'M_{k,2}\\big({\\rm Sp}(4,\\mathbb{Z})\\big)'           
            dimension = siegel_core._dimension_Sp4Z_2
            
        elif 'Sp6Z' == args['group']:
            info['parent_as_tex'] = 'M_k\\big({\\rm Sp}(6,\\mathbb{Z})\\big)'
            dimension = siegel_core._dimension_Sp6Z
            
        elif 'Sp8Z' == args['group']:
            info['parent_as_tex'] = 'M_k\\big({\\rm Sp}(8,\\mathbb{Z})\\big)'
            dimension = siegel_core._dimension_Sp8Z
            
        elif 'Kp' == args['group']:
            info['parent_as_tex'] = 'M_k\\big(K(p)\\big)'
            info['learnmore'] += [ ('Paramodular forms', 'http://math.lfc.edu/~yuen/paramodular/')]
            info['generators'] = 'smf.Kp_generators'
            dimension = siegel_core._dimension_Kp

        elif 'Gamma0_2' == args['group']:
            info['parent_as_tex'] = 'M_k\\big(\\Gamma_0(2)\\big)'
            dimension = siegel_core._dimension_Gamma0_2
            
        elif 'Gamma0_3' == args['group']:
            info['parent_as_tex'] = 'M_k\\big(\\Gamma_0(3)\\big)'
            dimension = siegel_core._dimension_Gamma0_3
            
        elif 'Gamma0_3_psi_3' == args['group']:
            info['parent_as_tex'] = 'M_k\\big(\\Gamma_0(3,\\psi_3)\\big)'
            dimension = siegel_core._dimension_Gamma0_3_psi_3
            
        elif 'Gamma0_4' == args['group']:
            info['parent_as_tex'] = 'M_k\\big(\\Gamma_0(4)\\big)'
            dimension = siegel_core._dimension_Gamma0_4

        elif 'Gamma0_4_psi_4' == args['group']:
            info['parent_as_tex'] = 'M_k\\big(\\Gamma_0(4,\\psi_4)\\big)'
            dimension = siegel_core._dimension_Gamma0_4_psi_4

        elif 'Gamma0_4_half' == group:
            info['parent_as_tex'] =  'M_{k-1/2}\\big(\\Gamma_0(4)\\big)'
            dimension = siegel_core._dimension_Gamma0_4_half

        else:
            info['error'] = 'Request for unvalid type of Siegel modular form'
            return render_template("ModularForm_GSp4_Q/None.html", **info)

        info['learnmore'] += [ ('The spaces \('+info['parent_as_tex']+'\)', url_for( 'ModularForm_GSp4_Q_top_level', group = group, page='basic'))]
        bread += [( '\('+info['parent_as_tex']+'\)', url_for( 'ModularForm_GSp4_Q_top_level', group=group, page='forms'))]

    else:
        # some nonsense request came in
        return render_template("ModularForm_GSp4_Q/None.html")

        # We branch now according to the key 'page'


    if page == 'forms':
        try:
            f = urllib.urlopen( DATA + group +'/available_eigenforms.p')
            go = pickle.load(f)
            f.close()
            forms_exist = True
        except (IOError, EOFError, KeyError ):
            info['error'] = 'No data access'
            forms_exist = False
        if True == forms_exist:
            info['forms'] = [ (k,[(form,go[k][form]) for form in go[k]]) for k in go]
        return render_template( "ModularForm_GSp4_Q/ModularForm_GSp4_Q_forms.html", \
                                title = 'Siegel modular forms \(' + info['parent_as_tex'] + '\)', \
                                bread = bread, **info)


    if page == 'basic':
        bread += [( 'Basic information', url_for( 'ModularForm_GSp4_Q_top_level', group=group, page=page) )]
        return render_template( "ModularForm_GSp4_Q/ModularForm_GSp4_Q_basic.html", \
                                title = 'Siegel modular forms basic information', \
                                bread = bread, **info)

        
    if page == 'dimensions':
        if not weight_range:
            min_wt = 1; max_wt = 16
        else:
            info['weight_range'] = weight_range
            # parse weight_range
            wr = weight_range.split('-')
            try:
                wr = map( int, wr)
                min_wt = wr[0]
                if len(wr) == 1:
                    max_wt = min_wt
                    if min_wt > 1000000:
                        info['error'] = 'Input too large: Please enter a smaller number.'
                        min_wt = 2; max_wt = 50
                else:
                    max_wt = wr[1]
                    if max_wt-min_wt >= 0 and  (max_wt-min_wt + 1)*max_wt > 1000000:
                        min_wt = 2; max_wt = 50
                        info['error'] = 'Input too large: Please enter a smaller range.'
                        #raise ValueError('gaga')
            except ValueError, e:
                info['error'] = 'Invalid input: ' + e.message
                min_wt = 2; max_wt =50

##             if info['group'] == "Sp8Z":
##               info['table_headers'] = ["Weight", "Total", "Ikeda Lifts", "Miyawaki Lifts", "Other"]

        try:
            if 'Kp' == group:
                info['dimensions'] = [ (k, dimension( k, tp = int(level))) for k in range(min_wt, max_wt+1)]
                bread += [( 'Dimensions', \
                            url_for( 'ModularForm_GSp4_Q_top_level', group=group, page=page, level=level, weight_range = weight_range))]
            else:
                info['dimensions'] = [ (k, dimension( k)) for k in range(min_wt, max_wt+1)]
                bread += [( 'Dimensions', \
                            url_for( 'ModularForm_GSp4_Q_top_level', group=group, page=page, weight_range = weight_range))]
        except:
            info['error'] = 'Functional error'
        
        if 'Sp8Z' == group:
            info['table_headers'] = ['Weight', 'Total', 'Ikeda lifts', 'Miyawaki lifts', 'Other']

        elif group == 'Kp':
            info['table_headers'] = ["Weight", "Total", "Gritsenko Lifts", "Nonlifts", "Oldforms"]

        elif 'Gamma0_4_half' == group:
            info['table_headers'] = ['Weight', 'Total', 'Non cusp', 'Cusp']
            
        else:
            info['table_headers'] = ["Weight", "Total", "Eisenstein", "Klingen", "Maass", "Interesting"]

        return render_template( "ModularForm_GSp4_Q/ModularForm_GSp4_Q_dimensions.html", \
                                title = 'Siegel modular forms dimensions \(' + info['parent_as_tex'] + '\)', \
                                bread = bread, **info)


    if page == 'specimen':
        info['weight'] = weight

        # try to load data
        try:
            file_name = weight + '_' + form + '.sobj'
            f_url = DATA + group + '/eigenforms/' + file_name
            f = load(f_url)
            file_name = weight + '_' + form + '-ev.sobj'
            g_url = DATA + group +'/eigenvalues/' + file_name
            g =load( g_url)
            loaded = True
        except:
            info['error'] = 'Data not available'
            loaded = False

        if True == loaded:

            # throw out disc = 0 keys for cusp forms
            f_keys = f[2].keys()
            if  'Sp4Z' == group and 'E' != form and 'Klingen' != form:
                f_keys = filter( lambda (a,b,c): b^2<4*a*c, f_keys)
                
            # sort the table of Fourier coefficients by discriminant, forms in increasing lexicographic order
            if 'Sp8Z' != group: 
                our_cmp = lambda (a,b,c), (A,B,C) : cmp( (4*a*c - b**2,a,b,c), (4*A*C - B**2, A,B,C) )
                f_keys.sort( cmp = our_cmp)

            if 'Sp8Z' == group:
                # matrix index is given as [m11 m22 m33 m44 m12 m13 m23 m14 m24 m34]
                __mat = lambda (m11, m22, m33, m44, m12, m13, m23, m14, m24, m34): \
                        matrix( ZZ, 4,4, [m11,m12,m13,m14, m12,m22,m23,m24, m13,m23,m33,m34, m14,m24,m34,m44])
                __cmp = lambda f1, f2: cmp( [__mat(f1).det()]+list(f1), [__mat(f2).det()]+list(f2))
                f_keys.sort( cmp = __cmp)

            try:
                if not modulus:
                    m = 0
                else:
                    m = int( modulus)
                info['modulus'] = m
                if m != 0:
                    for i in f_keys:
                        f[2][i] = Integer(f[2][i])%m
            except:
                pass

            info['form'] = [ f[0].parent(), f[1], \
                             [ (l,g[1][l]) for l in g[1]], \
                             [(i,f[2][i]) for i in f_keys], \
                             f_url, g_url]
##             info['friends'] = [ ('Spin L-function', url_for('not_yet_implemented')), \
##                                 ('Standard L-function', url_for('not_yet_implemented')), \
##                                 ('First Fourier-Jacobi coefficient', url_for('not_yet_implemented'))]


        location = url_for( 'ModularForm_GSp4_Q_top_level', group=group, page=page, weight=weight, form=form)
        info['form_name'] = form
        bread += [( weight + '_' + form, location)]
        return render_template( "ModularForm_GSp4_Q/ModularForm_GSp4_Q_specimen.html", \
                                    title = 'Siegel modular form ' + weight + '_' + form, \
                                    bread = bread, **info)            

    # if a nonexisting page was requested return the homepage of Siegel modular forms
    return render_webpage()

